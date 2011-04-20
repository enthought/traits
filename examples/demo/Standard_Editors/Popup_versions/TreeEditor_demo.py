"""
Demonstrates using the TreeEditor to display a hierarchically organized data
structure.

In this case, the tree has the following hierarchy:
  - Partner
    - Company
      - Department
        - Employee
"""

from traits.api \
    import HasTraits, Str, Regex, List, Instance

from traitsui.api \
    import Item, View, TreeEditor, TreeNode

class Employee ( HasTraits ):
    name  = Str( '<unknown>' )
    title = Str
    phone = Regex( regex = r'\d\d\d-\d\d\d\d' )

    def default_title ( self ):
        self.title = 'Senior Engineer'

class Department ( HasTraits ):
    name      = Str( '<unknown>' )
    employees = List( Employee )

class Company ( HasTraits ):
    name        = Str( '<unknown>' )
    departments = List( Department )
    employees   = List( Employee )

# Create an empty view for objects that have no data to display:
no_view = View()

# Define the TreeEditor used to display the hierarchy:
tree_editor = TreeEditor(
    nodes = [
        TreeNode( node_for  = [ Company ],
                  auto_open = True,
                  children  = '',
                  label     = 'name',
                  view      = View( [ 'name' ] )
        ),
        TreeNode( node_for  = [ Company ],
                  auto_open = True,
                  children  = 'departments',
                  label     = '=Departments',
                  view      = no_view,
                  add       = [ Department ]
        ),
        TreeNode( node_for  = [ Company ],
                  auto_open = True,
                  children  = 'employees',
                  label     = '=Employees',
                  view      = no_view,
                  add       = [ Employee ]
        ),
        TreeNode( node_for  = [ Department ],
                  auto_open = True,
                  children  = 'employees',
                  label     = 'name',
                  view      = View( [ 'name' ] ),
                  add       = [ Employee ]
        ),
        TreeNode( node_for  = [ Employee ],
                  auto_open = True,
                  label     = 'name',
                  view      = View( [ 'name', 'title', 'phone' ] )
        )
    ]
)

class Partner ( HasTraits ):
    name    = Str( '<unknown>' )
    company = Instance( Company )

    view = View(
        Item( name       = 'company',
              editor     = tree_editor,
              show_label = False
        ),
        title     = 'Company Structure',
        buttons   = [ 'OK' ],
        resizable = True,
        style     = 'custom',
        width     = .3,
        height    = .3
    )

# Create an example data structure:
jason  = Employee( name  = 'Jason',
                   title = 'Senior Engineer',
                   phone = '536-1057' )
mike   = Employee( name  = 'Mike',
                   title = 'Senior Engineer',
                   phone = '536-1057' )
dave   = Employee( name  = 'Dave',
                   title = 'Senior Software Developer',
                   phone = '536-1057' )
martin = Employee( name  = 'Martin',
                   title = 'Senior Engineer',
                   phone = '536-1057' )
duncan = Employee( name  = 'Duncan',
                   title = 'Consultant',
                   phone = '526-1057' )

# Create the demo:
popup = Partner(
    name    = 'Enthought, Inc.',
    company = Company(
        name        = 'Enthought',
        employees   = [ dave, martin, duncan, jason, mike ],
        departments = [
            Department(
                name      = 'Business',
                employees = [ jason, mike ]
            ),
            Department(
                name      = 'Scientific',
                employees = [ dave, martin, duncan ]
            )
        ]
    )
)

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

