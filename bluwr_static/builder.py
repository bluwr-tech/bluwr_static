class ComponentVariableNotFound(Exception):
    ...

class ElementFileNotFound(Exception):
    ...

class VariablesMatcher:
    """docstring for VariablesMatcher"""
    def __init__(self):
        self.pattern = r'(\{\{.*?\}\})'
        
    def find(self, text):
        import re

        res = {}
        matches = re.findall(self.pattern, text)
        for match in matches:
            striped = match.replace("{{", "").replace("}}", "").strip()
            res[striped] = match 
            
        return res

class ComponentMatcher:
    def __init__(self):
        import re
        self.pattern = r'(?s)(\{\{.*?\}\})'
        self.types = {}
        self.matches = {}

    def find(self, text, conjugate=False):
        import re
        import yaml

        self.matches = {}
        matches = re.findall(self.pattern, text)

        for match in matches:
            yaml_text = (
                match
                .replace("{{", "", 1)
                .replace("}}", "", 1)
                # .replace("/t", "  ")
                .strip()
            )

            data = yaml.safe_load(yaml_text)
            name = None
            if type(data) is dict:
                name = list(data.keys())[0]
                self.types[name] = data[name]
            elif type(data) is str:
                name=data
                self.types[name] = None
            else:
                raise TypeError(f"Unknown type, matche: {data}")

            key = hash(match)
            self.matches[key] = {"insert": match, "values": self.types[name], "component": name}
            
        return self.matches

    def __getitem__(self, insert):
        key = hash(insert)
        return self.matches[key]

def get_filename(file_path):
    import os

    name = os.path.splitext(os.path.basename(file_path))[0]
    return name

class Component(object):
    """docstring for Component"""
    def __init__(self, file, default_value=""):
        super(Component, self).__init__()
        self.file = file
        self.variables = {}
        self.default_value=""
        self.template = ""

        self.load()

    def load(self):
        matcher = VariablesMatcher()

        with open(self.file, 'r') as fil:
            self.template = fil.read()

        self.variables = matcher.find(self.template)
    
    def build(self, variable_values:dict):
        res = str(self.template)
        
        if not variable_values is None:
            for variable in variable_values.keys():
                if not variable in self.variables:
                    raise ComponentVariableNotFound(f"Cannot find variable {variable} in component {self.file}")

            for var_name, inline in self.variables.items():
                try:
                    value = variable_values[var_name]
                except KeyError:
                    value = self.default_value

                res = res.replace(inline, str(value))

        return res

class Files(object):
    """docstring for Files"""
    def __init__(self, class_type):
        super(Files, self).__init__()
        self.files = {}
        self.class_type = class_type

    def add_file(self, fil):
        with open(fil, "r"):
            file_name = get_filename(fil)
            self.files[file_name] = self.class_type(fil)
        return self

    def add_folder(self, folder, extension):
        import glob
      
        glob_path = f"{folder}/*.{extension}"
        files = glob.glob( glob_path )
        for fil in files:
            self.add_file(fil)
        return self

    def __getitem__(self, name):
        try:
            return self.files[name]
        except KeyError:
            raise ElementFileNotFound(f"Cannot find element file {name}")

class Page(object):
    """docstring for Page"""
    def __init__(self, file):
        super(Page, self).__init__()
        self.file = file
        self.template = None
        self.matcher = ComponentMatcher()
        self.load()

    def load(self):
        with open(self.file, 'r') as fil:
            self.template = fil.read()

        self.component_inserts = self.matcher.find(self.template)

    def build(self, components, sections):
        res = str(self.template)
        for match in self.matcher.matches.values():
            if sections and (match["component"] in sections.files):
                if match["component"] is self:
                    raise ValuError(f"recurssive call of {match['component']}")

                section = sections[ match["component"] ]
                to_insert = section.build( components, sections )
            else:
                component = components[ match["component"] ]
                to_insert = component.build(match["values"])
            to_replace = match["insert"]
            res = res.replace(to_replace, to_insert)

        return res

class Builder(object):
    """docstring for Builder"""
    def __init__(self):
        super(Builder, self).__init__()
        self.components = Files(class_type=Component)
        self.pages = Files(class_type=Page)
        self.sections = Files(class_type=Page)

    def load_components(self, folder):
        print(f"loading components from: {folder}")
        self.components.add_folder(folder=folder, extension="html")
        return self
    
    def load_sections(self, folder):
        print(f"loading sections from: {folder}")
        self.sections.add_folder(folder=folder, extension="html")
        return self
    
    def load_pages(self, folder):
        print(f"loading pages from: {folder}")
        self.pages.add_folder(folder=folder, extension="html")
        return self

    def build(self, folder="./"):
        import os

        os.makedirs(folder, exist_ok=True)
        for file_name, page in self.pages.files.items():
            print(f"building page {file_name}")
            res_page = page.build(self.components, self.sections)

            path = os.path.join(folder, file_name) + ".html"
            with open(path, "w") as fil:
                fil.write(res_page)


if __name__ == '__main__':
    builder = Builder()
    builder.load_components("./template/components")
    builder.load_sections("./template/sections")
    builder.load_pages("./template/pages")
    builder.build()
