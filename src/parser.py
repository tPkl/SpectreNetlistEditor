import pyparsing as _p
from netlister import *
from netlister.netlist import Netlist
from netlister.subcircuit import Subcircuit as SubcircuitClass
from netlister.instance import Instance as InstanceClass

def parse_spectre(netlist_string: str):
    # newlines are part of the grammar, thus redifine the whitespaces without it
    ws = ' \t'
    _p.ParserElement.setDefaultWhitespaceChars(ws)

    # spectre netlist grammar definition
    EOL = _p.LineEnd().suppress() # end of line
    linebreak = _p.Suppress("\\" + _p.LineEnd()) # breaking a line with backslash newline
    identifier=_p.Word(_p.alphanums+'_!\\<>') # a name for...
    number=_p.Word(_p.nums + ".") # a number
    net = identifier # a net
    nets = _p.Group(_p.OneOrMore(net('net'))) # many nets
    cktname = identifier # name of a subcircuit
    cktname_end = _p.Keyword("ends").suppress()
    comment = _p.Suppress("//" + _p.SkipTo(_p.LineEnd()))
    
    meta_library = _p.Suppress("//") + _p.Suppress(_p.Literal("Library name:")) + _p.SkipTo(EOL)("library") + EOL
    meta_cell =    _p.Suppress("//") + _p.Suppress(_p.Literal("Cell name:")) + _p.SkipTo(EOL)("cell") + EOL
    meta_view =    _p.Suppress("//") + _p.Suppress(_p.Literal("View name:")) + _p.SkipTo(EOL)("view") + EOL
    subckt_meta =  _p.Optional(meta_library) + _p.Optional(meta_cell) + _p.Optional(meta_view)

    top_meta_library = _p.Suppress("//") + _p.Suppress(_p.Literal("Design library name:")) + _p.SkipTo(EOL)("design_library") + EOL
    top_meta_cell =    _p.Suppress("//") + _p.Suppress(_p.Literal("Design cell name:")) + _p.SkipTo(EOL)("design_cell") + EOL
    top_meta_view =    _p.Suppress("//") + _p.Suppress(_p.Literal("Design view name:")) + _p.SkipTo(EOL)("design_view") + EOL
    design_meta =      top_meta_library | top_meta_cell | top_meta_view

    expression = _p.Word(_p.alphanums+'._*+-/()"')
    point_list = _p.Group(_p.Suppress("[") + _p.ZeroOrMore(identifier | number) + _p.Suppress("]"))
    inst_param_key = identifier + _p.Suppress("=")
    inst_param_value = point_list('expression') | expression('expression')
    inst_parameter = _p.Group(inst_param_key('name') + inst_param_value('value')).setResultsName('key')
    parameters = _p.Group(_p.ZeroOrMore(inst_parameter)).setResultsName('parameters')
    instref = identifier
    instname = identifier
    instance = _p.Group(instname('name') + _p.Suppress('(') + nets('nets') + _p.Suppress(')') + instref('reference') + parameters + EOL).setResultsName('instance')
    subcircuit_content = _p.Group(_p.OneOrMore(instance | EOL | comment)).setResultsName('subnetlist')
    subcircuit = _p.Group(
        subckt_meta
        # matches subckt <name> <nets> <newline>
        + _p.Keyword("subckt").suppress() + cktname('name') + nets('nets') + EOL  
        # matches the content of the subcircuit
        + subcircuit_content
        # matches ends <name> <newline>
        + cktname_end + _p.matchPreviousExpr(cktname).suppress() + EOL).setResultsName('subcircuit')
    
    #instance.setDebug(True)
    
    # simulator settings grammar definitions
    simulator_declaration = (
        _p.Keyword("simulator").suppress()
        + _p.Keyword("lang").suppress()
        + _p.Suppress("=")
        + _p.Word(_p.alphanums+"_")
        + EOL
    ).setResultsName("simulator_declaration")
    
    global_declaration = _p.Group(
        _p.Keyword("global").suppress()
        + nets
        + EOL
    ).setResultsName("global_declaration")
    
    parameters_declaration = _p.Group(
        _p.Keyword("parameters").suppress()
        + _p.OneOrMore(inst_parameter)
        + EOL
    )
    
    include_declaration = _p.Group(
        _p.Keyword("include").suppress()
        + _p.Suppress('"')
        + _p.Word(_p.alphanums+"./_$-")
        + _p.Suppress('"')
        + _p.ZeroOrMore(
            _p.Keyword("section")
            + _p.Suppress("=")
            + _p.Word(_p.alphanums+"_")
        )
        + EOL
    ).setResultsName("include_declaration")
    
    simopts_declaration = _p.Group(
        _p.Keyword("simulatorOptions").suppress()
        + _p.Suppress("options")
        + parameters
        + EOL
    ).setResultsName("simopts_declaration")
    
    trancheck_declaration = _p.Group(
        _p.Keyword("tranCheckLimit").suppress()
        + _p.Suppress("checklimit")
        + parameters
        + EOL
    ).setResultsName("trancheck_declaration")
    
    tranoptions_declaration = _p.Group(
        _p.Keyword("tran").suppress()
        + _p.Suppress("tran")
        + parameters
        + EOL
    ).setResultsName("tranoptions_declaration")
    
    primitives_declaration = _p.Group(
        _p.Keyword("primitives").suppress()
        + _p.Suppress("info")
        + parameters
        + EOL
    ).setResultsName("primitives_declaration")
    
    subckts_declaration = _p.Group(
        _p.Keyword("subckts").suppress()
        + _p.Suppress("info")
        + parameters
        + EOL
    ).setResultsName("subckts_declaration")
    
    design_declaration = _p.Group(
        _p.Keyword("designParamVals").suppress()
        + _p.Suppress("info")
        + parameters
        + EOL
    ).setResultsName("design_declaration")
    
    asserts_declaration = _p.Group(
        _p.Keyword("asserts").suppress()
        + _p.Suppress("info")
        + parameters
        + EOL
    ).setResultsName("asserts_declaration")
    
    save_list = _p.Group(
        _p.Keyword("save").suppress()
        + _p.ZeroOrMore(_p.Word(_p.alphanums+'_!\\<>:.'))
        + EOL
    ).setResultsName("save_list")
    
    saveopts_declaration = _p.Group(
        _p.Keyword("saveOptions").suppress()
        + _p.Suppress("options")
        + parameters
        + EOL
    ).setResultsName("saveopts_declaration")
    
    simulator_options = simulator_declaration | global_declaration | parameters_declaration \
                      | include_declaration | simopts_declaration | trancheck_declaration \
                      | tranoptions_declaration | primitives_declaration | subckts_declaration \
                      | design_declaration | asserts_declaration | save_list \
                      | saveopts_declaration
    
    top_level_element = _p.Group(_p.ZeroOrMore(subcircuit_content)).setResultsName('top_level')
    
    netlist_element = design_meta | instance | subcircuit | EOL | comment('comment') | simulator_options
    netlist = _p.ZeroOrMore(netlist_element) + _p.StringEnd()
    
    netlist.ignore(linebreak)
    
    parameters.setParseAction(handle_parameters)
    instance.setParseAction(handle_instance)
    subcircuit.setParseAction(handle_subcircuit)

    raw_results = netlist.parseString(netlist_string)
    
    nl = Netlist()
    if "design_library" in raw_results:
        nl.library = str(raw_results.design_library).strip()
    if "design_cell" in raw_results:
        nl.cell = str(raw_results.design_cell).strip()
    if "design_view" in raw_results:
        nl.view = str(raw_results.design_view).strip()

    for element in raw_results:
        if isinstance(element, SubcircuitClass):
            nl.subcircuits[element.name] = element
        elif isinstance(element, InstanceClass):
            nl.top_level_instances.append(element)
        elif isinstance(element, _p.ParseResults):
            name = element.getName()
            if name == "global_declaration":
                nl.global_nets.extend(list(element[0]))
            elif name == "include_declaration":
                nl.includes.append(list(element))
            elif name in ["simulator_declaration", "simopts_declaration", "trancheck_declaration", "tranoptions_declaration", "saveopts_declaration"]:
                nl.simulator_options.append({name: list(element)})
            elif name in ["primitives_declaration", "subckts_declaration", "design_declaration", "asserts_declaration", "save_list"]:
                nl.analyses.append({name: list(element)})

    return nl

def parse_hspice(netlist_string: str):
    # newlines are part of the grammar, thus redifine the whitespaces without it
    ws = ' \t'
    _p.ParserElement.setDefaultWhitespaceChars(ws)

    # spectre netlist grammar definition
    EOL = _p.LineEnd().suppress() # end of line
    linebreak = _p.Suppress(_p.LineEnd() + "+") # breaking a line with backslash newline
    identifier=_p.Word(_p.alphanums+'_!<>#') # a name for...
    number=_p.Word(_p.nums + ".") # a number
    net = identifier # a net
    nets = _p.Group(_p.OneOrMore(net('net') + ~_p.FollowedBy("=") | linebreak)) # many nets
    cktname = identifier # name of a subcircuit
    cktname_end = _p.CaselessLiteral(".ends").suppress()
    comment = _p.Suppress("//" + _p.SkipTo(_p.LineEnd())) | _p.Suppress("*" + _p.SkipTo(_p.LineEnd()))
    expression = _p.Word(_p.alphanums+'._*+-/()')
    inst_param_key = identifier + _p.Suppress("=")
    inst_param_value = expression('expression')
    inst_parameter = _p.Group(inst_param_key('name') + inst_param_value('value')).setResultsName('key')
    parameters = _p.Group(_p.ZeroOrMore(inst_parameter | linebreak)).setResultsName('parameters')
    instname = identifier
    instnets = _p.Group(_p.OneOrMore(net('net') + ~_p.FollowedBy("=") | linebreak))
    instance = _p.Group(instname('name') + instnets('instnets') + parameters + EOL).setResultsName('instance')
    subcircuit_content = _p.Group(_p.ZeroOrMore(instance | EOL | comment)).setResultsName('subnetlist')
    subcircuit = _p.Group(
        # matches subckt <name> <nets> <newline>
        _p.CaselessLiteral(".subckt").suppress() + cktname('name') + nets('nets') + EOL  
        # matches the content of the subcircuit
        + subcircuit_content
        # matches ends <name> <newline>
        + cktname_end + _p.matchPreviousExpr(cktname).suppress() + EOL).setResultsName('subcircuit')
    netlist_element = subcircuit | instance | EOL | comment('comment')
    netlist = _p.ZeroOrMore(netlist_element) + _p.StringEnd()
    
    parameters.setParseAction(handle_parameters)
    instance.setParseAction(handle_instance)
    subcircuit.setParseAction(handle_subcircuit)

    return netlist.parseString(netlist_string);

def handle_parameters(token):
    d = {}
    for p in token.parameters:
        d[p[0]] = p[1]
    return d

def handle_subcircuit(token):
    sc = token.subcircuit
    nets = sc.nets
    name = sc.name
    instances = sc.subnetlist
    
    library = str(sc.library).strip() if sc.library else None
    cell = str(sc.cell).strip() if sc.cell else None
    view = str(sc.view).strip() if sc.view else None
    
    s = SubcircuitClass(name, nets, instances, library=library, cell=cell, view=view)
    return [s]

def handle_instance(token):
    inst = token.instance
    name = inst.name
    if inst.nets: # this is the case for spectre
        pins = inst.nets
        reference = inst.reference
    elif inst.instnets: # this is the case for hspice
        pins = inst.instnets[0:-1]
        reference = inst.instnets[-1]
    parameters = inst.parameters
    i = InstanceClass(name, pins, reference, parameters)
    return [i]

