import prettytable


def _word_wrap(string, max_length=0):
    if max_length <= 0:
        return string
    return '\n'.join([string[i:i + max_length] for i in
                     range(0, len(string), max_length)])

def print_dict(d, wrap=0):
    pt = prettytable.PrettyTable(['Property', 'Value'],
                                 caching=False, print_empty=False)
    pt.aligns = ['l', 'l']
    for (prop, value) in d.iteritems():
        if value is None:
            value = ''
        value = _word_wrap(value, max_length=wrap)
        pt.add_row([prop, value])
    print pt.get_string(sortby='Property')


def print_list(objs, fields, formatters={}):
    pt = prettytable.PrettyTable([f for f in fields], caching=False)
    pt.aligns = ['l' for f in fields]

    for o in objs:
        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                field_name = field.lower().replace(' ', '_')
                data = getattr(o, field_name, '') or o.get(field_name, '') 
                if data is None:
                    data = ''
                row.append(data)
        pt.add_row(row)
    print pt.get_string(sortby=fields[0])

if __name__ == '__main__':
    data={"name":"coocla","email":"32792324242@qq.com","phone":123456789}
    data=[{"name":"coocla","age":24},{"name":"coocla","age":24}]
    if isinstance(data, list):
        print_list(data, ("name","age"))
    else:
        print_dict(data)
