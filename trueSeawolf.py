import ply
import sys
from ply import yacc
import ply.lex as lex

################################################################################
# Shakeeb Saleh 109239204
#
#
#
################################################################################

reserved = {
    'or': 'OR',
    'not': 'NOT',
    'and' : 'AND',
    'in' : 'IN',
    'if': 'IF',
    'while': 'WHILE',
    'print' : 'PRINT',
    'else': 'ELSE',
    'return':'RETURN'
}

tokens = ['LPAREN', #)
'RPAREN', # (
'RBRACKET', # [
'LBRACKET', # ]
'LCURLY', # {
'RCURLY', # }
'SEMICOLON', # ;
'COMMA', # ,
'ID', # var x
'REAL', # d.dd
'NUMBER', #d
'STRING', # %s
'PLUS', # +
'UMINUS', # -x
'MINUS', # -
'TIMES', # *
'DIVIDE', # /
'INTDIVIDE', # //
'MODULUS', # %
'EXPONENT', # **
'EQUALS', # =
'LT', # < Less Than
'LTE', # <= Less Than Equal
'GT', # > Greater Than
'GTE', # >= greater Than Equals
'NE', # <> not equals
'EE', # == double equals
] + list(reserved.values()) #all possible tokens

#all possible tokens defined here
t_ignore = ' \t\n'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_RBRACKET = r'\]'
t_LBRACKET = r'\['
t_LCURLY = r'{'
t_RCURLY = r'}'
t_COMMA = r'\,'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'\/'
t_INTDIVIDE = r'\/\/'
t_MODULUS = r'\%'
t_EXPONENT = r'\*\*'
t_EQUALS = r'='
t_SEMICOLON = r';'
t_IN = r'in'
t_LT = r'<'
t_LTE = r'<='
t_GT = r'>'
t_GTE = r'>='
t_NE = r'<>'
t_EE = r'=='
t_NOT = r'not'
t_AND = r'and'
t_OR = r'or'
t_IF = r'if'
t_ELSE = r'else'
t_PRINT = r'print'
t_WHILE = r'while'


#regular expression code with some action rule
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t
def t_REAL(t):
    r'\d*\.\d+'
    t.value = float(t.value)
    return t
#def t_newline(t):
#    r'\n+'
#    t.lexer.lineno += len(t.value)
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID') #check for reserved words
    return t
def t_STRING(t):
    r'\"[^\"]+\"|\"\"'
    t.value = str(t.value[1:-1])
    return t

#error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lex.lex() #builds lexer

#global scope
global_variables = dict()
#stack
frame = list() #to access the current frame, do frame[len(frame-1)]
frame.append(global_variables)

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'NOT'),
    ('left', 'LT', 'LTE', 'GT', 'GTE', 'NE', 'EE'),
    ('left', 'IN'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'INTDIVIDE'),
    ('left', 'EXPONENT'),
    ('left', 'MODULUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('nonassoc', 'LPAREN', 'RPAREN'),
    ('nonassoc', 'LBRACKET', 'RBRACKET'),
    ('nonassoc', 'UMINUS')
)

def p_program(p):
    """
    program : stmts
    """
    p[0] = run(p[1])

def p_stmts(p): # block stmts conditional stmts loop stmts
    """
    stmts   : stmt SEMICOLON stmts
            | block stmts
            | conditional stmts
            | loop stmts
            | function stmts
            | empty
    """
    if(len(p) == 4):
        p[0] = ("stmt", p[1], p[3])
    elif(len(p) == 3):
        p[0] = ("stmt", p[1], p[2])
    elif((len(p) != 4) or (len(p) != 3)):
        p[0] = p[1]

def p_conditional(p):
    """
    conditional : IF LPAREN expression RPAREN block
                | IF LPAREN expression RPAREN block ELSE block
    """
    if(len(p) == 6):
        p[0] = (p[1], p[3], p[5])
    elif (len(p) == 8):
        p[0] = ('ifelse', p[3], p[5], p[7])

def p_loop(p):
    """
    loop    : WHILE LPAREN expression RPAREN block
    """
    p[0] = (p[1], p[3], p[5])

def p_block(p):
    """
    block   : LCURLY stmts RCURLY
    """
    p[0] = p[2]

def p_stmt(p):
    """
    stmt    : expression
            | assignment
            | print
            | return

    """
    p[0] = p[1]

def p_function(p):
    """
    function    : ID LPAREN parameters RPAREN block
                | ID LPAREN RPAREN block
    """
    # parse through params as list, construct tuple
    if(len(p) == 6):
        p[0] = ('fxndef', p[1], p[3], p[5])
    elif(len(p) == 5):
        p[0] = ('fxndef', p[1], [], p[4])

def p_parameters(p):
    """
    parameters : parameters COMMA ID
                | ID
    """
    if(len(p) == 4):
        p[0] = p[1] + [p[3]]
    elif(len(p) == 2):
        p[0] = [p[1]]

def p_return(p):
    """
    return  : RETURN expression
    """
    p[0] = ('ret', p[2])

def p_print(p):
    """
    print : PRINT LPAREN expression RPAREN
    """
    p[0] = (p[1], p[3])

def p_functioncall(p):
    """
    functioncall    : ID LPAREN list RPAREN
                    | ID LPAREN RPAREN
    """
    if(len(p) == 5):
        p[0] = ('fxncall', p[1], p[3])
    elif(len(p) == 4):
        p[0] = ('fxncall', p[1], [])

def p_expression(p):
    """
    expression  : logical
                | mathexpression
                | comparison
                | factor
                | lentry
                | lindex
                | functioncall
    """
    if(len(p) == 2):
        p[0] = p[1]

def p_lindex(p):
    """
    lindex : expression LBRACKET expression RBRACKET
    """
    p[0] = ('index', p[1],p[3])

def p_logical(p):
    """
    logical : NOT expression
            | expression AND expression
            | expression OR expression
            | expression IN expression
    """
    if (len(p) == 2): # comparison
        p[0] = p[1]
    elif (len(p) == 3): # not logical
        p[0] = ('not', p[2])
    elif (len(p) == 4):  # logical and comparison || logical or comparison
        if (p[2] == 'and'):
            p[0] = ('and',p[1],p[3])
        elif(p[2] == 'or'):
            p[0] = ('or', p[1], p[3])
        elif(p[2] == 'in'): # in only works for strings in strings, or things in lists
            p[0] = ('in',p[1] ,p[3])

def p_comparison(p): # comparisons can only exist between integers, however this might give me errors
    """
    comparison  : expression LT expression
                | expression LTE expression
                | expression GT expression
                | expression GTE expression
                | expression NE expression
                | expression EE expression
    """
    p[0] = (p[2], p[1], p[3])

def p_assignment(p):
    """
    assignment  : ID EQUALS expression
                | expression LBRACKET expression RBRACKET EQUALS expression
    """
    if(len(p) == 4):
        p[0] = (p[2] , p[1], p[3])
    elif(len(p) == 7):
        p[0] = ("ie", p[1], p[3], p[6])
    #global_variables[p[1]] = p[3]
    #print(global_variables)

def p_mathexpression(p):
    """
    mathexpression  : expression PLUS expression
                | expression TIMES expression
                | expression MINUS expression
                | expression DIVIDE expression
                | expression INTDIVIDE expression
                | expression EXPONENT expression
                | expression MODULUS expression
                | MINUS factor %prec UMINUS
    """
    if(len(p) == 4): #if input length is 4 then it must be exp = exp
        p[0] = (p[2], p[1], p[3])
    elif(len(p) == 2):
        p[0] = p[1]
    elif(len(p) == 3):
        p[0] = ('um', p[1],p[2])

def p_factor(p):# need to add list indexing to this
    """
    factor  : LPAREN expression RPAREN
            | NUMBER
            | REAL
            | STRING
            | variable
    """
    if(len(p) == 4): # parentesized expression
        p[0] = p[2]
    elif(len(p) == 2):
        p[0] = p[1]

def p_variable(p):
    """
    variable : ID
    """
    p[0] = ('get', p[1])

def p_lentry(p):
    """
    lentry  : LBRACKET RBRACKET
            | LBRACKET list RBRACKET
    """
    if(len(p) == 3): #empty List
        p[0] = []
    elif(len(p) == 4):
        p[0] = p[2]
    else:
        pass

def p_list(p):
    """
    list    : listhead elem
    """
    if(len(p) == 3):
        p[0] = p[1] + p[2]

def p_listhead(p):
    """
    listhead    : listhead elem COMMA
                | empty
    """
    if(len(p) == 4): #here p2 is a list and p1 appears to be none all the time
        p[0] = p[1]+p[2]
    elif(len(p) == 2):
        p[0] = []

def p_elem(p):
    """
    elem    : expression
    """
    p[0] = [p[1]]

def p_error(p):
    raise ValueError('syntax error')

def p_empty(p):
    """
    empty   :
    """
    pass

def sameType(A, B): #this just checks that the types are equivalent between A and B
    if isinstance(B, type(A)):
        return True
    else:
        return False

parser = yacc.yacc()

def run(p):
    global global_variables
    global frame
    #print(p)
    if(type(p) == tuple):
        print(p)
        if(p[0] == '<'):
            return int(bool(run(p[1]) < run(p[2])))
        elif(p[0] == '<='):
            return int(bool(run(p[1]) <= run(p[2])))
        elif(p[0] == '>'):
            return int(bool(run(p[1]) > run(p[2])))
        elif(p[0] == '>='):
            return int(bool(run(p[1]) >= run(p[2])))
        elif(p[0] == '<>'):
            return int(bool(run(p[1]) != run(p[2])))
        elif(p[0] == '=='):
            return int(bool(run(p[1]) == run(p[2])))
        elif(p[0] == '+' ): # can add 2 strings 2 lists. if int or real, then its cool, but gotta check for both lists and strings
            return run(p[1]) + run(p[2])
        elif(p[0] == 'um'):
            return -1*run(p[2])
        elif(p[0] == '-'):
            return run(p[1]) - run(p[2])
        elif(p[0] == '*'):
            return run(p[1]) * run(p[2])
        elif(p[0] == '/'):
            return run(p[1]) / run(p[2])
        elif (p[0] == '//'):
            return run(p[1]) // run(p[2])
        elif (p[0] == '**'):
            return run(p[1]) ** run(p[2])
        elif (p[0] == '%'):
            return run(p[1]) % run(p[2])
        elif (p[0] == 'ie'): # index list
            if(p[1][1] in global_variables):
                global_variables[run(p[1][1])][run(p[2])] = run(p[3])
            elif(p[1][1] in frame[len(frame)-1]):
                frame[len(frame)-1][run(p[1][1])][run(p[2])] = run(p[3])
            else:
                raise ValueError("error")
        elif (p[0] == '=' ): # this needs to be changed to account for the existence of a call stack'
            # = name value
            if(p[1] not in global_variables):
                frame[len(frame)-1][p[1]] = run(p[2])
            else:
                global_variables[run(p[1])] = run(p[2])
        elif (p[0] == 'print'):
            print(run(p[1]))
            return
        elif (p[0] == 'stmt'):
            if(len(p) == 3):
                run(p[1])
                if ('1return' not in frame[len(frame)-1]):
                    run(p[2])
        elif (p[0] == 'get'): # check for in global
            if(p[1] in frame[len(frame)-1]):
                return frame[len(frame)-1][p[1]]
            elif(p[1] in global_variables):
                return global_variables[p[1]]
            else:
                print("waka waka")
                #raise TypeError('oh no')
        elif (p[0] == 'if'): # if, condition, then, other things
            if(run(p[1])):
                run(p[2])
        elif(p[0] == 'ifelse'):
            if(run(p[1])):
                run(p[2])
            else:
                run(p[3])
        elif(p[0] == 'while'):
            while(run(p[1])):
                run(p[2])
        elif(p[0] == 'not'):
            return (int(bool(not run(p[1]))))
        elif(p[0] == 'and'):
            return (int(bool(run(p[1]) and run(p[2]))))
        elif(p[0] == 'or'):
            return (int(bool(run(p[1]) or run(p[2]))))
        elif(p[0] == 'in'):
            return (int(bool(run(p[1]) in run(p[2]))))
        elif(p[0] == 'index'):
            return run(p[1])[run(p[2])]
        elif(p[0] == 'fxncall'): # fxncall, fxnname, params as list
            # put the name value pairs in the dictionary
            #first, grab the fxn from the symbol table using it's name, always in p[1], otherwise errorout
            if(p[1] in global_variables):
                #it exists as a fxn, okay so grab the definition
                # make sure the number of arguments are consistent
                fdef = global_variables[p[1]]
                #print("function definition is", fdef)
                if(len(fdef[2]) == len(p[2])):
                    nf = dict()
                    #print("HEY", fdef[2])
                    for i in range(len(fdef[2])):
                        nf[fdef[2][i]] = run(p[2][i])
                    #variables mapped
                    #print(nf)
                    frame.append(nf)
                    run(fdef[3]) # run the body
                    # check for the existence of a return value-- if it exists return it
                    if('1return' in frame[len(frame)-1]):
                        val = frame[len(frame)-1]['1return']
                        frame.pop()
                        return val
                    else:
                        None
                else:
                    raise ValueError("incorrent number of args")
            else:
                raise ValueError("fxn doesnt exist")
        elif(p[0] == 'fxndef'):
            global_variables[p[1]] = p # fxndef, fxnname, params as list, body
        elif(p[0] == 'ret'):
            frame[len(frame)-1]['1return'] = run(p[1])
            #frame[len(frame)-1]['isreturn'] = 1
    else:
        return p

def main(argv):
    filename = ''
    if(len(sys.argv) > 1):
        filename = sys.argv[1]
    iF = open(argv[1], 'r')
    # l = ''
    # for line in iF:
    #     l+=line
    try:
        result = parser.parse(iF.read())
    except ZeroDivisionError as error:
        print('Syntax Error',str(error))
    except ValueError as error:
        print(str(error))
    except TypeError as error:
        print('Semantic error', str(error))
    iF.close()

if __name__ == '__main__':
	main(sys.argv)
