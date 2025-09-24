grammar Kaos;

goal    : subgoal (BOOL_OP subgoal)* (PARALLEL_OP goal)*;

subgoal : TEMP_OP IDENTIFIER 'BY' subgoal
        | TEMP_OP IDENTIFIER 'USING' agent
        ;

agent   : IDENTIFIER ;

BOOL_OP    : 'AND'
           | 'OR'
           ;

PARALLEL_OP : '||' ;

TEMP_OP    : 'ACHIEVE'
           | 'MAINTAIN'
           | 'AVOID'
           ;
IDENTIFIER  : [a-zA-Z_][a-zA-Z0-9_]*;

WS          : [ \t\r\n]+ -> skip;