import boto3

class BedrockAgent:
    def __init__(self, agent_id, agent_alias_id, region):
        self.agent_client = boto3.Session(region_name=region).client('bedrock-agent-runtime')
        self.agent_id = agent_id
        self.agent_alias_id = agent_alias_id

    def invoke(self, query, session_id):
        ref = None
        if query is None or query == "":
            return "", ref

        # invoke the agent API
        agent_response = self.agent_client.invoke_agent(
            inputText=query,
            agentId=self.agent_id,
            agentAliasId=self.agent_alias_id,
            sessionId=session_id,
            enableTrace=True
        )
        event_stream = agent_response['completion']
        agent_answer = ""
        try:
            for event in event_stream:
                if 'chunk' in event:
                    data = event['chunk']['bytes']
                    print(f"Final answer ->\n{data.decode('utf8')}")
                    agent_answer = data.decode('utf8')
                elif 'trace' in event:
                    print(event['trace'])
                    if 'orchestrationTrace' in event['trace']['trace'].keys():
                        if 'observation' in event['trace']['trace']['orchestrationTrace'].keys():
                            if ('knowledgeBaseLookupOutput' in
                                    event['trace']['trace']['orchestrationTrace']['observation'].keys()):
                                refs = event['trace']['trace']['orchestrationTrace']['observation'][
                                    'knowledgeBaseLookupOutput']['retrievedReferences']
                                ref = refs[0]['location']['s3Location']['uri']
                                print(ref)
                else:
                    print("unexpected event.", event)
        except Exception as e:
            print("unexpected event.", e)
            agent_answer = str(e)
        print(agent_answer)
        agent_answer = agent_answer.replace("$", "\$")
        return agent_answer, ref


def parse_trace(trace):
    current_step = ""
    if 'trace' in trace:
        trace_message = trace['trace']
        if 'orchestrationTrace' in trace_message:
            orchestration_trace = trace_message['orchestrationTrace']
            print("=======================")
            print(orchestration_trace)
            print("=======================")
            if 'modelInvocationInput' in orchestration_trace:
                current_step = "Executing orchestration step..."
                model_invocation_input = orchestration_trace['modelInvocationInput']
                if 'type' in model_invocation_input:
                    model_invocation_type = model_invocation_input['type']
                    if model_invocation_type == "PRE_PROCESSING":
                        current_step = "Executing pre-processsing step"
                    elif model_invocation_type == "ORCHESTRATION":
                        current_step = "Thinking about next step..."
                    elif model_invocation_type == "KNOWLEDGE_BASE_RESPONSE_GENERATION":
                        current_step = "Generating response from knowledge base"
                    elif model_invocation_type == "POST_PROCESSING":
                        current_step = "Executing post-processsing step"
            elif 'rationale' in orchestration_trace:
                rationale = orchestration_trace['rationale']
                current_step = ""
                if rationale['text']:
                    current_step = "Reasoning for next steps: " + rationale['text'].replace("\n", " ")
            elif 'invocationInput' in orchestration_trace:
                invocation_input = orchestration_trace['invocationInput']
                current_step = "Invoking action group or knowledge base"
                if 'invocationType' in invocation_input:
                    invocation_type = invocation_input['invocationType']
                    if invocation_type == "KNOWLEDGE_BASE":
                        current_step = "Invoking knowledge base"
                        if 'knowledgeBaseLookupInput' in invocation_input:
                            kb_lookup_input = invocation_input['knowledgeBaseLookupInput']
                            if kb_lookup_input['text']:
                                current_step = "Searching knowledge base for \"" + kb_lookup_input['text'].replace("\n", " ") + "\""
                    elif invocation_type == "ACTION_GROUP":
                        current_step = "Invoking action group"
                        if 'actionGroupInvocationInput' in invocation_input:
                            ag_inv_input = invocation_input['actionGroupInvocationInput']
                            if ag_inv_input['apiPath']:
                                current_step = "Invoking action group API " + ag_inv_input['apiPath'].replace("\n", " ")
            elif 'observation' in orchestration_trace:
                observation = orchestration_trace['observation']
                current_step = "Processing the output of an action group, knowledge base, or the response"
                if 'type' in observation:
                    observation_type = observation['type']
                    if observation_type == "ACTION_GROUP":
                        current_step = "Processing action group output"
                    elif observation_type == "KNOWLEDGE_BASE":
                        current_step = "Processing knowledge base output"
                    elif observation_type == "FINISH":
                        current_step = "Generating final response"
        elif 'postProcessingTrace' in trace_message:
            current_step = "Executing post-processing step, shaping the response"
        elif 'preProcessingTrace' in trace_message:
            current_step = "Executing pre-processing step, contextualizing and categorizing the inputs"
    return current_step