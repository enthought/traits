"""
This is a demonstration of the Event Monitor tool, which allows you to see the
sequence of Traits notification events generated within a running application.

This tool is currently still under development, but since it already provides 
some useful functionality, it is being presented in its current state.

When the Event Monitor first appears, it is disabled, meaning that notification
events are not being monitored. To start monitoring events, simply check the
<b>Enabled</b> check box. To disable monitoring again, simply uncheck the 
checkbox.

As events occur they are added to the bottom of the table view. Each row
in the table contains the following information:
    
    * <b>Class</b>: The class name of the object generating the event.
    * <b>Object Id</b>: The object id of the object generating the event.
    * <b>Name</b>: The name of the object trait generating the event.
    * <b>Old</b>: The previous value of the trait generating the event.
    * <b>New</b>: The new value of the trait generating the event.
    * <b>Depth</b>: The recursion depth of the event.
    * <b>Timestamp</b>: The time at which the event occurred. Times are in 
      seconds from when the event monitor started.

You can control how many events are logged by the value set in the <b>Maximum
events</b> field. The default value is 30, but any value in the range from 1 
to 100,000 can be specified.

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

