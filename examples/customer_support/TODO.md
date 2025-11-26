# Items still to do for the customer service bot

### Customer service bot functionality

[ ] Modify tools so they change the data (next up for Laine)
  [ ] EscalateToSpecialistTool: make this a real tool functionality? Would need to add people to data.json
  [ ] CreateFollowUpTaskTool: create a new KB article? this would be neat

### Framework functionality

[ ] Figure out why a failing activity ends the workflow - easiest way to test this is to remove a registered action/tool, it will fail on run_execution_agent

[ ] Clean up README because this is complex, yo

[ ] Add proactive monitoring agent

[ ] Look at adding the stuff in customer_support/ui/backend to the framework

[ ] Run on Temporal Cloud

[ ] MCP? 
  [ ] Query learning

[ ] Add ability to approve/deny specific solutions?

### UI changes

[ ] Add sweet sweet 80s synthesizer theme to UI and data

[ ] Change Load Workflow section in the UI header to load a list of workflows (drop down, get workflows from namespace) and then change the Monitor Workflow and Impact Analysis pages accordingly

[ ] Add link on Monitor Workflow page to go to workflow history

### Other

[ ] Look at READMEs and try to untangle to make instructions to run more clear

[ ] Probably there should be some tests I guess?