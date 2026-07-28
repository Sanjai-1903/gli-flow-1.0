import re
from pathlib import Path


CLOCK_NAMES = re.compile(r"^(clk|clock|i_clk|sys_clk|sysclk|core_clk|clk_i|clk_in)$", re.IGNORECASE)
RESET_NAMES = re.compile(r"^(rst|reset|rst_n|rstn|reset_n|i_rst|rst_i|rstn_i|resetn|arst|aresetn|areset)$", re.IGNORECASE)


def _strip_comments(text):
    text = re.sub(r"//.*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return text


def _find_files(directory, pattern=r"\.(v|sv|vh|svh)$"):
    directory = Path(directory)
    files = []
    for f in sorted(directory.rglob("*")):
        if f.is_file() and re.search(pattern, f.suffix, re.IGNORECASE):
            files.append(f)
    return files


_MODULE_RE = re.compile(
    r"module\s+(\w+)\s*(?:#\s*\(.*?\))?\s*\(",
    re.DOTALL,
)

_PORT_DECL_RE = re.compile(
    r"(input|output|inout)\s+(wire|reg|logic|tri|wand|wor|supply0|supply1|tri0|tri1|triand|trior|trireg)?\s*(?:\[([^\]]*)\])?\s*(\w+)",
)


def _collect_module_instances(text):
    inst_re = re.compile(r"(\w+)\s+(?:#\s*\(.*?\)\s*)?(\w+)\s*\(", re.DOTALL)
    instances = set()
    for m in inst_re.finditer(text):
        module_name = m.group(1)
        if module_name not in ("module", "endmodule", "if", "for", "while", "case", "assign", "always", "initial", "function", "task", "generate", "begin", "fork", "join"):
            instances.add(module_name)
    return instances


_PARAM_PORT_RE = re.compile(
    r"module\s+(\w+)\s*(?:#\s*\(.*?\))?\s*\(",
    re.DOTALL,
)

_CLOSE_PAREN_RE = re.compile(r"\)\s*;")


def _extract_module_body(text, start_pos):
    depth = 0
    in_paren = False
    for i in range(start_pos, len(text)):
        ch = text[i]
        if ch == "(":
            depth += 1
            in_paren = True
        elif ch == ")":
            depth -= 1
            if depth == 0 and in_paren:
                return text[start_pos:i+1]
    return text[start_pos:]


class ModuleInfo:
    def __init__(self, name, ports, file_path):
        self.name = name
        self.ports = ports
        self.file_path = file_path

    @property
    def clock_ports(self):
        return [p for p in self.ports if p.is_clock]

    @property
    def reset_ports(self):
        return [p for p in self.ports if p.is_reset]

    def to_dict(self):
        return {
            "name": self.name,
            "file": str(self.file_path),
            "ports": [p.to_dict() for p in self.ports],
            "clock_ports": [p.name for p in self.clock_ports],
            "reset_ports": [p.name for p in self.reset_ports],
        }


class PortInfo:
    def __init__(self, name, direction, width, file_path):
        self.name = name
        self.direction = direction
        self.width = width
        self.file_path = file_path

    @property
    def is_clock(self):
        return CLOCK_NAMES.match(self.name) is not None

    @property
    def is_reset(self):
        return RESET_NAMES.match(self.name) is not None

    def to_dict(self):
        return {
            "name": self.name,
            "direction": self.direction,
            "width": self.width,
        }


def parse_file(file_path):
    text = Path(file_path).read_text()
    text = _strip_comments(text)

    modules = []
    pos = 0

    while True:
        m = _MODULE_RE.search(text, pos)
        if not m:
            break

        module_name = m.group(1)
        port_list_start = m.end()

        port_list_text = _extract_module_body(text, port_list_start - 1)
        port_list_end = port_list_start + len(port_list_text) - 1
        if port_list_end > len(text):
            port_list_end = len(text)

        ports = []
        for pm in _PORT_DECL_RE.finditer(port_list_text):
            direction = pm.group(1)
            width_str = pm.group(3)
            port_name = pm.group(4)

            width = None
            if width_str:
                width = width_str.strip()
            ports.append(PortInfo(port_name, direction, width, file_path))

        modules.append(ModuleInfo(module_name, ports, file_path))

        module_end = text.find("endmodule", m.start())
        if module_end == -1:
            break
        pos = module_end + 9

    return modules


def scan_directory(directory):
    files = _find_files(directory)
    all_modules = {}
    all_instances = set()

    for f in files:
        mods = parse_file(f)
        for mod in mods:
            all_modules[mod.name] = mod
        text = _strip_comments(f.read_text())
        all_instances.update(_collect_module_instances(text))

    top_candidates = [name for name in all_modules if name not in all_instances]

    top_module = None
    if len(top_candidates) == 1:
        top_module = all_modules[top_candidates[0]]
    elif len(top_candidates) > 1:
        top_module = all_modules[top_candidates[0]]

    rtl_files = [str(f) for f in files]

    return all_modules, top_module, rtl_files


def detect_from_directory(directory):
    all_modules, top_module, rtl_files = scan_directory(directory)

    manifest = {}

    if rtl_files:
        manifest["rtl_files"] = rtl_files

    if top_module:
        manifest["top_module"] = top_module.name
        manifest["design_name"] = top_module.name

        if top_module.clock_ports:
            manifest["clock_port"] = top_module.clock_ports[0].name

        clock_port_obj = next((p for p in top_module.ports if p.is_clock), None)
        if clock_port_obj and clock_port_obj.width == "0":
            pass

    if not manifest.get("design_name") and rtl_files:
        manifest["design_name"] = Path(directory).name

    return manifest
