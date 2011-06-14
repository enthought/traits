requirements = [
    ('AppTools', '3.4.1'),
    ('BlockCanvas', '3.2.1'),
    ('Chaco', '3.4.0'),
    ('CodeTools', '3.2.0'),
    ('Enable', '3.4.0'),
    ('EnthoughtBase', '3.1.0'),
    ('EnvisageCore', '3.2.0'),
    ('EnvisagePlugins', '3.2.0'),
    ('ETSDevTools', '3.1.1'),
    ('etsproxy', '0.1.0'),
    ('GraphCanvas', '3.0.0'),
    ('Mayavi', '3.4.1'),
    ('pyface', '3.6.0'),
    ('SciMath', '3.0.7'),
    ('traits', '3.6.0'),
    ('traitsui', '3.6.0'),
]

INFO = {
    'name': 'ETS',
    'version': '3.6.1',
    'install_requires': ['%s >= %s.dev' % nv for nv in requirements],
}
