class AstBaseTraverser:
    '''The base class for all other traversers.'''

    def __init__(self):
        pass
        # A unit test now calls self.check_visitor_names().
    
    def attribute_base(self,node):
        
        '''Return the node representing the base of the chain.
        Only 'Name' and 'Builtin' nodes represent names.
        All other chains have a base that is a constant or nameless dict, list, etc.
        '''

        trace = False
        kind = self.kind(node)
        if kind in ('Name','Builtin','Str'):
            result = node # We have found the base.
        elif kind in ('Attribute','Subscript'):
            result = self.attribute_base(node.value)
        elif kind == 'Call':
            result = self.attribute_base(node.func)
        else:
            # The chain is rooted in a constant or nameless dict, list, etc.
            # This is not an error.
            # g.trace('*** kind: %s node: %s' % (kind,node))
            result = node
        return result

    def attribute_target(self,node):
        
        '''Return the node representing the target of the chain.
        Only 'Name' and 'Builtin' Ops represent names.'''
        
        trace = True
        kind = self.kind(node)
        if kind in ('Name','Builtin','Str'):
            result = node # We have found the target.
        elif kind == 'Attribute':
            # result = self.attribute_target(node.attr) ### Always a string.
            result = node # node.attr is the target.
        elif kind == 'Call':
            result = self.attribute_target(node.func)
        elif kind == 'Subscript':
            result = self.attribute_target(node.value)
        else:
            assert(False)
            # Don't call u.format here.
            return None

        return result
    #@+node:ekr.20130315140102.9529: *4* bt.check_visitor_names
    def check_visitor_names(self,silent=False):
        
        '''Check that there is an ast.AST node named x
        for all visitor methods do_x.'''
        
        #@+<< define names >>
        #@+node:ekr.20130315140102.9531: *5* << define names >>
        names = (
            'Add','And','Assert','Assign','Attribute','AugAssign','AugLoad','AugStore',
            'BinOp','BitAnd','BitOr','BitXor','BoolOp','Break',
            'Builtin', ### Python 3.x only???
            'Bytes', # Python 3.x only.
            'Call','ClassDef','Compare','Continue',
            'Del','Delete','Dict','DictComp','Div',
            'Ellipsis','Eq','ExceptHandler','Exec','Expr','Expression','ExtSlice',
            'FloorDiv','For','FunctionDef','GeneratorExp','Global','Gt','GtE',
            'If','IfExp','Import','ImportFrom','In','Index','Interactive',
            'Invert','Is','IsNot','LShift','Lambda',
            'List','ListComp','Load','Lt','LtE',
            'Mod','Module','Mult','Name','Not','NotEq','NotIn','Num',
            'Or','Param','Pass','Pow','Print',
            'RShift','Raise','Repr','Return',
            'Set','SetComp','Slice','Store','Str','Sub','Subscript','Suite',
            'Try', # Python 3.x only.
            'TryExcept','TryFinally','Tuple','UAdd','USub','UnaryOp',
            'While','With','Yield',
            # Lower case names...
            'arg',           # A valid ast.AST node: Python 3.
            'alias',         # A valid ast.AST node.
            'arguments',     # A valid ast.AST node.
            'comprehension', # A valid ast.AST node.
            'keyword',       # A valid ast.AST node(!)
                # 'keywords', # A valid field, but not a valid ast.AST node!
                # In ast.Call nodes, node.keywords points to a *list* of ast.keyword objects.
            # There is never any need to traverse these:
                # 'id','n','name','s','str'.
        )
        #@-<< define names >>
        #@+<< Py2K grammar >>
        #@+node:ekr.20130315140102.9530: *5* << Py2k grammar >>
        #@@nocolor-node
        #@+at
        # See
        # mod:
        #     Expression(expr body)
        #     Interactive(stmt* body)
        #     Module(stmt* body)
        #     Suite(stmt* body) #  not an actual node,
        # stmt:
        #     Assert(expr test, expr? msg)
        #     Assign(expr* targets, expr value)
        #     AugAssign(expr target, operator op, expr value)
        #     Break
        #     ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)
        #     Continue
        #     Delete(expr* targets)
        #     Exec(expr body, expr? globals, expr? locals)
        #     Expr(expr value)
        #     For(expr target, expr iter, stmt* body, stmt* orelse)
        #     FunctionDef(identifier name, arguments args,stmt* body, expr* decorator_list)
        #     Global(identifier* names)
        #     If(expr test, stmt* body, stmt* orelse)
        #     Import(alias* names)
        #     ImportFrom(identifier? module, alias* names, int? level)
        #     Pass
        #     Print(expr? dest, expr* values, bool nl)
        #     Raise(expr? type, expr? inst, expr? tback)
        #     Return(expr? value)
        #     TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)
        #     TryFinally(stmt* body, stmt* finalbody)
        #     While(expr test, stmt* body, stmt* orelse)
        #     With(expr context_expr, expr? optional_vars, stmt* body)
        # expr:
        #     Attribute(expr value, identifier attr, expr_context ctx)
        #     BinOp(expr left, operator op, expr right)
        #     BoolOp(boolop op, expr* values)
        #     Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)
        #     Compare(expr left, cmpop* ops, expr* comparators)
        #     Dict(expr* keys, expr* values)
        #     DictComp(expr key, expr value, comprehension* generators)
        #     GeneratorExp(expr elt, comprehension* generators)
        #     IfExp(expr test, expr body, expr orelse)
        #     Lambda(arguments args, expr body)
        #     List(expr* elts, expr_context ctx) 
        #     ListComp(expr elt, comprehension* generators)
        #     Name(identifier id, expr_context ctx)
        #     Num(object n) -- a number as a PyObject.
        #     Repr(expr value)
        #     Set(expr* elts)
        #     SetComp(expr elt, comprehension* generators)
        #     Str(string s) -- need to specify raw, unicode, etc?
        #     Subscript(expr value, slice slice, expr_context ctx)
        #     Tuple(expr* elts, expr_context ctx)
        #     UnaryOp(unaryop op, expr operand)
        #     Yield(expr? value)
        # expr_context:
        #     AugLoad
        #     AugStore
        #     Del
        #     Load
        #     Param
        #     Store
        # slice:
        #     Ellipsis
        #     Slice(expr? lower, expr? upper, expr? step) 
        #     ExtSlice(slice* dims) 
        #     Index(expr value) 
        # boolop:
        #     And | Or 
        # operator:
        #     Add | Sub | Mult | Div | Mod | Pow | LShift | RShift | BitOr | BitXor | BitAnd | FloorDiv
        # unaryop:
        #     Invert | Not | UAdd | USub
        # cmpop:
        #     Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn
        # excepthandler:
        #     ExceptHandler(expr? type, expr? name, stmt* body)
        #     
        # Lower case node names:
        #     alias (identifier name, identifier? asname)
        #     arguments (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)
        #     comprehension (expr target, expr iter, expr* ifs)
        #     keyword (identifier arg, expr value)
        #@-<< Py2K grammar >>
        #@+<< Py3K grammar >>
        #@+node:ekr.20130320161725.9543: *5* << Py3k grammar >>
        #@@nocolor-node
        #@+at
        # 
        #     mod = Module(stmt* body)
        #         | Interactive(stmt* body)
        #         | Expression(expr body)
        # 
        #         -- not really an actual node but useful in Jython's typesystem.
        #         | Suite(stmt* body)
        # 
        #     stmt = FunctionDef(identifier name, arguments args, 
        #                            stmt* body, expr* decorator_list, expr? returns)
        #           | ClassDef(identifier name, 
        #              expr* bases,
        #              keyword* keywords,
        #              expr? starargs,
        #              expr? kwargs,
        #              stmt* body,
        #              expr* decorator_list)
        #           | Return(expr? value)
        # 
        #           | Delete(expr* targets)
        #           | Assign(expr* targets, expr value)
        #           | AugAssign(expr target, operator op, expr value)
        # 
        #           -- use 'orelse' because else is a keyword in target languages
        #           | For(expr target, expr iter, stmt* body, stmt* orelse)
        #           | While(expr test, stmt* body, stmt* orelse)
        #           | If(expr test, stmt* body, stmt* orelse)
        #           | With(withitem* items, stmt* body)
        # 
        #           | Raise(expr? exc, expr? cause)
        #           | Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
        #           | Assert(expr test, expr? msg)
        # 
        #           | Import(alias* names)
        #           | ImportFrom(identifier? module, alias* names, int? level)
        # 
        #           | Global(identifier* names)
        #           | Nonlocal(identifier* names)
        #           | Expr(expr value)
        #           | Pass | Break | Continue
        # 
        #           -- XXX Jython will be different
        #           -- col_offset is the byte offset in the utf8 string the parser uses
        #           attributes (int lineno, int col_offset)
        # 
        #           -- BoolOp() can use left & right?
        #     expr = BoolOp(boolop op, expr* values)
        #          | BinOp(expr left, operator op, expr right)
        #          | UnaryOp(unaryop op, expr operand)
        #          | Lambda(arguments args, expr body)
        #          | IfExp(expr test, expr body, expr orelse)
        #          | Dict(expr* keys, expr* values)
        #          | Set(expr* elts)
        #          | ListComp(expr elt, comprehension* generators)
        #          | SetComp(expr elt, comprehension* generators)
        #          | DictComp(expr key, expr value, comprehension* generators)
        #          | GeneratorExp(expr elt, comprehension* generators)
        #          -- the grammar constrains where yield expressions can occur
        #          | Yield(expr? value)
        #          | YieldFrom(expr value)
        #          -- need sequences for compare to distinguish between
        #          -- x < 4 < 3 and (x < 4) < 3
        #          | Compare(expr left, cmpop* ops, expr* comparators)
        #          | Call(expr func, expr* args, keyword* keywords,
        #              expr? starargs, expr? kwargs)
        #          | Num(object n) -- a number as a PyObject.
        #          | Str(string s) -- need to specify raw, unicode, etc?
        #          | Bytes(bytes s)
        #          | Ellipsis
        #          -- other literals? bools?
        # 
        #          -- the following expression can appear in assignment context
        #          | Attribute(expr value, identifier attr, expr_context ctx)
        #          | Subscript(expr value, slice slice, expr_context ctx)
        #          | Starred(expr value, expr_context ctx)
        #          | Name(identifier id, expr_context ctx)
        #          | List(expr* elts, expr_context ctx) 
        #          | Tuple(expr* elts, expr_context ctx)
        # 
        #           -- col_offset is the byte offset in the utf8 string the parser uses
        #           attributes (int lineno, int col_offset)
        # 
        #     expr_context = Load | Store | Del | AugLoad | AugStore | Param
        # 
        #     slice = Slice(expr? lower, expr? upper, expr? step) 
        #           | ExtSlice(slice* dims) 
        #           | Index(expr value) 
        # 
        #     boolop = And | Or 
        # 
        #     operator = Add | Sub | Mult | Div | Mod | Pow | LShift 
        #                  | RShift | BitOr | BitXor | BitAnd | FloorDiv
        # 
        #     unaryop = Invert | Not | UAdd | USub
        # 
        #     cmpop = Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn
        # 
        #     comprehension = (expr target, expr iter, expr* ifs)
        # 
        #     excepthandler = ExceptHandler(expr? type, identifier? name, stmt* body)
        #                     attributes (int lineno, int col_offset)
        # 
        #     arguments = (arg* args, identifier? vararg, expr? varargannotation,
        #                      arg* kwonlyargs, identifier? kwarg,
        #                      expr? kwargannotation, expr* defaults,
        #                      expr* kw_defaults)
        #     arg = (identifier arg, expr? annotation)
        # 
        #     -- keyword arguments supplied to call
        #     keyword = (identifier arg, expr value)
        # 
        #     -- import name with optional 'as' alias.
        #     alias = (identifier name, identifier? asname)
        # 
        #     withitem = (expr context_expr, expr? optional_vars)
        #@-<< Py3K grammar >>

        # Inexpensive, because there are few entries in aList.
        aList = [z for z in dir(self) if z.startswith('do_')]
        for s in sorted(aList):
            name = s[3:]
            if name not in names:
                if not silent:
                    assert(False)
                assert False,name
                    # This is useful now that most errors have been caught.

    def find_function_call (self,node):
        '''
        Return the static name of the function being called.
        
        tree is the tree.func part of the Call node.'''
        

        kind = self.kind(node)
        assert kind not in ('str','Builtin')
        if kind == 'Name':
            s = node.id
        elif kind == 'Attribute':
            s = node.attr # node.attr is always a string.
        elif kind == 'Call':
            s = self.find_function_call(node.func)
        elif kind == 'Subscript':
            s = None
        else:
            s = None
        return s or '<no function name>'

    def info (self,node):
        return '%s: %9s' % (node.__class__.__name__,id(node))

    def kind(self,node):
        return node.__class__.__name__

    def op_name (self,node,strict=True):
        '''Return the print name of an operator node.'''
        
        d = {
        # Binary operators. 
        'Add':       '+',
        'BitAnd':    '&',
        'BitOr':     '|',
        'BitXor':    '^',
        'Div':       '/',
        'FloorDiv':  '//',
        'LShift':    '<<',
        'Mod':       '%',
        'Mult':      '*',
        'Pow':       '**',
        'RShift':    '>>',
        'Sub':       '-',
        # Boolean operators.
        'And':   ' and ',
        'Or':    ' or ',
        # Comparison operators
        'Eq':    '==',
        'Gt':    '>',
        'GtE':   '>=',
        'In':    ' in ',
        'Is':    ' is ',
        'IsNot': ' is not ',
        'Lt':    '<',
        'LtE':   '<=',
        'NotEq': '!=',
        'NotIn': ' not in ',
        # Context operators.
        'AugLoad':  '<AugLoad>',
        'AugStore': '<AugStore>',
        'Del':      '<Del>',
        'Load':     '<Load>',
        'Param':    '<Param>',
        'Store':    '<Store>',
        # Unary operators.
        'Invert':   '~',
        'Not':      ' not ',
        'UAdd':     '+',
        'USub':     '-',
        }
        name = d.get(self.kind(node),'<%s>' % node.__class__.__name__)
        if strict: assert name,self.kind(node)
        return name