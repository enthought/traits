"""
Also, please note that in order for this demo to run, you must have the 
enthought.developer package installed.
"""

try:
        
    from enthought.developer.tools.event_monitor \
        import EventMonitor
    
    # Create an instance of the EventMonitor tool:
    demo = EventMonitor()
except:
    raise Exception( 'This demo requires the enthought.developer package '
                     'to be installed.' )
        
# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

