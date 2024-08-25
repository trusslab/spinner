import json

context_hierarchy = {'P': 0, 'S': 1, 'H':2, 'NMI':3}

def transform_context(type_context):
    irqs_hierarchy = {'.': 0, 'b':1, 'd':2}
   
    for progtype in type_context:
        if irqs_hierarchy[type_context[progtype][1]]>context_hierarchy[type_context[progtype][0]]:
            if type_context[progtype][1] == 'b':
                type_context[progtype] = 'S'
            else:
                type_context[progtype] = 'H'
        else:
            type_context[progtype] = type_context[progtype][0]
    return type_context


def helper_context():
    with open('../fptests/output/helper-progtype-copy.json', 'r') as file:
       helper_progtype = json.load(file)
    with open('../utils/output/prog_type-context.json', 'r') as file:
        progtype_context = json.load(file)
    progtype_context = transform_context(progtype_context)

    helper_context = {}
    for helper in helper_progtype:
        context = ''
        for progtype in progtype_context:
            if progtype not in helper_progtype[helper][0] and progtype not in helper_progtype[helper][1]:
                print(progtype+" not in dynamic analysis")
            if progtype in helper_progtype[helper][0]:
                if context=='':
                    context = progtype_context[progtype]
                if context_hierarchy[progtype_context[progtype]]>context_hierarchy[context]:
                    context = progtype_context[progtype]
        helper_context[helper] = context

    print(helper_context)
    return helper_context



if __name__ == "__main__":
    helper_context()
