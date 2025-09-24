from lark import Lark, Tree

class DSL:

    def __init__(self,req):

        # Define the grammar
        self.grammar = r"""
        start          : (goal)+
        goal           : temporal_op objective "by" refined_goal "in scenario where" scenario
        refined_goal   : objective "using" agent ("operationalized as" operation)? 
                       | (refined_goal "followed by" refined_goal)* 
                       | (refined_goal "parallely" refined_goal)*

        operation      : task ("if" condition)? "performed by" module "taking input" input ("&" input)* "producing output" output ("&" output)*   
                       | (operation "triggering" operation)* 
                    #    | (operation "achieving" objective)* 

        temporal_op    : "ACHIEVE" 
                       | "MAINTAIN" 

        objective      : STRING
                       | objective ("&" objective)*

        condition      : STRING 
                       | condition ("&" condition)*
                       | condition ("|" condition)*

        agent          : STRING
        task           : STRING 
                       | task ("&" task)*
        module         : STRING
        scenario       : STRING
        input          : STRING
        output         : STRING

        %import common.ESCAPED_STRING   -> STRING
        %import common.WS
        %ignore WS
        """

        # Instantiate the parser
        self.parser = Lark(self.grammar, start="goal")
        self.requirement = req
        self.parse_tree = self.verify_grammar()

    def verify_grammar(self):
        try:
            self.requirement = self.requirement
            sparse_tree = self.parser.parse(self.requirement)
            return sparse_tree
        except:
            return None
        
    def get_perception_model(self):

        for _st in self.parse_tree.iter_subtrees():
            if isinstance(_st, Tree) and _st.data=='refined_goal':
                for _stt in _st.children:
                    if isinstance(_stt, Tree) and _stt.data=='operation':
                        for _sttt in _stt.children:
                            if isinstance(_sttt, Tree)and _sttt.data=='operation':
                                task = _sttt.children[0]
                                module = _sttt.children[1]
                                try:
                                    if task.children[0][1:-1] == "Detect Pedestrian":
                                        return module.children[0][1:-1]
                                except:
                                    return None
                                
    def get_scenario(self):

        # print("I'm in scenario")

        for _st in self.parse_tree.iter_subtrees():
            if isinstance(_st, Tree) and _st.data=='scenario':
                for _stt in _st.children:
                    print(_stt[1:-1])
                    return _stt[1:-1]
                

