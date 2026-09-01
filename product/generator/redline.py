import io, re, sys, difflib, zipfile, shutil

def blocks(md):
    """Reviewable units: a table row is one, a paragraph is one."""
    out=[]
    for para in re.split(r'\n\s*\n', md):
        p=para.strip()
        if not p: continue
        if p.lstrip().startswith('|'):
            for line in p.split('\n'):
                if line.strip().startswith('|'): out.append(line.strip())
        else:
            out.append(re.sub(r'\s+',' ',p))
    return out

def norm(t):
    # Pipes go too. A markdown table row arrives as '| a | b |' and the same row in the
    # .docx arrives as its cell text with no delimiters at all, so leaving them in means
    # no table row ever matches — which is exactly what the first run reported: 0 rows.
    # Pandoc applies smart quotes, so the .md's straight ' and " arrive in the .docx as
    # curly ones and any changed block containing an apostrophe fails to match. Fold them,
    # and the dashes with them, before comparing.
    for a,b in (('\u2019',"'"),('\u2018',"'"),('\u201c','"'),('\u201d','"'),
                ('\u2014','-'),('\u2013','-'),('\u2026','...')):
        t=t.replace(a,b)
    t=re.sub(r'`|\*|_|~~|>|#','',t)
    t=t.replace('|',' ')
    t=re.sub(r'\s+',' ',t)
    return t.strip().lower()

def changed_units(old_md, new_md):
    A,B=blocks(old_md),blocks(new_md)
    sm=difflib.SequenceMatcher(None,[norm(x) for x in A],[norm(x) for x in B])
    out=[]
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag in ('replace','insert'):
            out += [norm(b) for b in B[j1:j2]]
    return [u for u in out if u]

RED='<w:color w:val="B00000"/>'

def colour_runs(xml_fragment):
    """Add a red colour to every run in this fragment."""
    def fix(m):
        run=m.group(0)
        if RED in run:
            return run
        if '<w:rPr>' in run:
            # At the END of rPr, not the start. OOXML fixes the order of rPr's children —
            # rStyle, rFonts, b, i, ... then color — and a colour placed before <w:b/> is
            # out of schema order. Word renders it anyway; LibreOffice silently ignores it,
            # so the run is red in the XML and black on the page. Only caught by rendering.
            return run.replace('</w:rPr>', RED+'</w:rPr>', 1)
        return run.replace('<w:r>', '<w:r><w:rPr>'+RED+'</w:rPr>', 1)
    return re.sub(r'<w:r>.*?</w:r>', fix, xml_fragment, flags=re.S)

def text_of(frag):
    """Text of a fragment, with a space at every paragraph boundary.

    Two traps, both of which silently produced zero table-row matches:
    <w:t[^>]*> also matches <w:tc>, <w:tr> and <w:tbl>, so the lazy .*?</w:t> after it
    swallows a whole table and returns raw XML as the "text"; and inserting a separator
    into the XML between tags does nothing, because only what sits inside <w:t> is ever
    captured. So split on the paragraph boundary first, then extract, then join.
    """
    cells=[]
    for para in frag.split('</w:p>'):
        s=''.join(re.findall(r'<w:t(?:\s[^>]*)?>(.*?)</w:t>', para, re.S))
        if s.strip(): cells.append(s)
    s=' '.join(cells)
    return norm(s.replace('&amp;','&').replace('&lt;','<').replace('&gt;','>')
                 .replace('&quot;','"').replace('&apos;',"'"))

def patch(docx, units):
    z=zipfile.ZipFile(docx); parts={n:z.read(n) for n in z.namelist()}; z.close()
    t=parts['word/document.xml'].decode('utf-8')
    hits=[0,0]

    def do_row(m):
        frag=m.group(0); txt=text_of(frag)
        if txt and any(txt==u or (len(txt)>20 and txt in u) for u in units):
            hits[0]+=1; return colour_runs(frag)
        return frag
    t=re.sub(r'<w:tr\b.*?</w:tr>', do_row, t, flags=re.S)

    # paragraphs outside tables: split on tables first
    pieces=re.split(r'(<w:tbl>.*?</w:tbl>)', t, flags=re.S)
    for i,pc in enumerate(pieces):
        if pc.startswith('<w:tbl>'): continue
        def do_p(m):
            frag=m.group(0); txt=text_of(frag)
            if txt and len(txt)>12 and any(txt==u or txt in u or u in txt for u in units):
                hits[1]+=1; return colour_runs(frag)
            return frag
        pieces[i]=re.sub(r'<w:p\b[^>]*>.*?</w:p>', do_p, pc, flags=re.S)
    t=''.join(pieces)

    parts['word/document.xml']=t.encode('utf-8')
    zo=zipfile.ZipFile(docx,'w',zipfile.ZIP_DEFLATED)
    for n,d in parts.items(): zo.writestr(n,d)
    zo.close()
    return hits
