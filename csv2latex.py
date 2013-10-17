import sublime, sublime_plugin
import re

def update_colwidth(colwidth, content):
    thiscolwidth = [len(s) for s in content]
    for i,w in enumerate(thiscolwidth):
        if i<len(colwidth):
            colwidth[i] = max(colwidth[i], w)
        else:
            colwidth.append(w)

def fill_spaces(content, colwidth):
    for j in range(len(content)):
        fill = colwidth[j]-len(content[j])
        content[j] = content[j] + " "*fill

class CsvToTableCommand(sublime_plugin.TextCommand):
    def make_table(self):
        view = self.view
        sel = view.sel()
        boolean = False
        if len(sel)==1:
            tabenv = view.find_all(r"\\begin\{tabular\*?\}(.|\n)*?\\end\{tabular\*?\}")
            if all([not tab.contains(sel[0]) for tab in tabenv]):
                boolean = True
        return boolean

    def add_double_bslash(self):
        view = self.view
        sel = view.sel()
        boolean = False
        if len(sel)==1:
            if sel[0].begin()==sel[0].end() or re.search(r"\\\\$", view.substr(sel[0]).strip()):
                boolean = True
        return boolean


    def run(self, edit, delim = "\t"):
        view = self.view
        # sublime.set_clipboard("a&bc\tedf few\nfew fefe\tfew")
        oldcb = sublime.get_clipboard()
        cb = oldcb
        cb = re.sub("&", r"\&", cb, flags=re.M)
        cb = re.sub("%", r"\%", cb, flags=re.M)
        sel =  view.sel()

        lines = [[s.strip() for s in re.split(r"(?<!\\)&", re.sub(delim, r"&", line, flags=re.M))]
                    for line in cb.split("\n")]

        nocol = max([len(line) for line in lines])
        for line in lines:
            line[:] = line if len(line)==nocol else line + [" "]*(nocol - len(line))
        colwidth = []
        for line in lines: update_colwidth(colwidth, line)
        for line in lines: fill_spaces(line, colwidth)


        if self.add_double_bslash():
            cb = " \\\\\n".join([" & ".join(line) for line in lines])+" \\\\"
        else:
            cb = "\n".join([" & ".join(line) for line in lines])

        if self.make_table():
            cb = "\\begin{tabular}{|" + "l"*nocol + "|}\n\\hline\n" + cb + "\n\\hline\n\\end{tabular}"

        # print(cb)
        sublime.set_clipboard(cb)
        view.run_command("paste")
        sublime.set_clipboard(oldcb)

    def is_enabled(self):
        view = self.view
        point = view.sel()[0].end()
        return view.score_selector(point, "text.tex.latex")>0

    def is_visible(self):
        view = self.view
        point = view.sel()[0].end()
        return view.score_selector(point, "text.tex.latex")>0