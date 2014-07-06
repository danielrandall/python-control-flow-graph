from src.traversers.astbasetraverser import AstBaseTraverser 
import ast
class AstFullTraverser(AstBaseTraverser):
    
    '''
    A super-fast tree traversal class.
    
    This class defines methods for *all* types of ast.Ast nodes,
    except nodes that typically don't need to be visited, such as nodes
    referenced by node.ctx and node.op fields.
    
    Subclasses are, of course, free to add visitors for, say, ast.Load,
    nodes. To make this work, subclasses must override visitors for
    ast.Node and ast.Attribute nodes so that they call::
        
        self.visit(node.ctx)
        
    At present, such calls are commented out.  Furthermore, if a visitor
    for ast.Load is provided, visitors for *all* kinds of nodes referenced
    by node.ctx fields must also be given.  Such is the price of speed.
    '''
    
    # def __init__(self):
        # AstBaseTraverser.__init__(self)

    def run(self,root):    
        # py==lint: disable=W0221
            # Arguments number differs from overridden method.
        self.visit(root)

    def do_Bytes(self,node): 
        pass # Python 3.x only.
        
    def do_Ellipsis(self,node):
        pass
        
    def do_Num(self,node):
        pass # Num(object n) # a number as a PyObject.
        
    def do_Str(self,node):
        pass # represents a string constant.
    
    def do_str(self, node):
        pass
    
    def do_Set(self, node):
        pass

    def do_arguments(self,node):
        for z in node.args:
            self.visit(z)
        for z in node.defaults:
            self.visit(z)
            
    # Python 3:
    # arg = (identifier arg, expr? annotation)

    def do_arg(self,node):
        if node.annotation:
            self.visit(node.annotation)

    def do_Attribute(self,node):
        self.visit(node.value)
        # self.visit(node.ctx)

    def do_BinOp (self,node):
        self.visit(node.left)
        # self.op_name(node.op)
        self.visit(node.right)

    def do_BoolOp (self,node): 
        for z in node.values:
            self.visit(z)

    def do_Call(self,node):
        
        self.visit(node.func)
        for z in node.args:
            self.visit(z)
        for z in node.keywords:
            self.visit(z)
        if getattr(node,'starargs',None):
            self.visit(node.starargs)
        if getattr(node,'kwargs',None):
            self.visit(node.kwargs)

    def do_Compare(self,node):
        self.visit(node.left)
        for z in node.comparators:
            self.visit(z)

    def do_comprehension(self,node):
        self.visit(node.target) # A name.
        self.visit(node.iter) # An attribute.
        for z in node.ifs:
            self.visit(z)

    def do_Dict(self,node):
        for z in node.keys:
            self.visit(z)
        for z in node.values:
            self.visit(z)

    def do_Expr(self,node):   
        self.visit(node.value)

    def do_Expression(self,node):
        '''An inner expression'''
        self.visit(node.body)

    def do_ExtSlice (self,node):
        for z in node.dims:
            self.visit(z)

    def do_GeneratorExp(self,node):
        self.visit(node.elt)
        for z in node.generators:
            self.visit(z)

    def do_IfExp (self,node):
        self.visit(node.body)
        self.visit(node.test)
        self.visit(node.orelse)

    def do_Index (self,node):  
        self.visit(node.value)

    def do_keyword(self,node):
        self.visit(node.value)


    def do_List(self,node):
        for z in node.elts:
            self.visit(z)
        # self.visit(node.ctx)

    def do_ListComp(self,node):
        elt = self.visit(node.elt)
        for z in node.generators:
            self.visit(z)

    def do_Name(self,node):
        # self.visit(node.ctx)
        pass

    # Python 2.x only
    # Repr(expr value)
    def do_Repr(self,node):
        self.visit(node.value)

    def do_Slice (self,node):
        if getattr(node,'lower',None):
            self.visit(node.lower)
        if getattr(node,'upper',None):
            self.visit(node.upper)
        if getattr(node,'step',None):
            self.visit(node.step)

    def do_Subscript(self,node):
        self.visit(node.value)
        self.visit(node.slice)
        # self.visit(node.ctx)

    def do_Tuple(self,node):
        for z in node.elts:
            self.visit(z)
        # self.visit(node.ctx)

    def do_UnaryOp (self,node):
        # self.op_name(node.op)
        self.visit(node.operand)

    def do_alias (self,node):
        # self.visit(node.name)
        # if getattr(node,'asname')
            # self.visit(node.asname)
        pass

    def do_Assert(self,node):
        self.visit(node.test)
        if node.msg:
            self.visit(node.msg)

    def do_Assign(self,node):
        for z in node.targets:
            self.visit(z)
        self.visit(node.value)

    def do_AugAssign(self,node):
        self.visit(node.target)
        self.visit(node.value)

    def do_Break(self,tree):
        pass

    def do_ClassDef (self,node):
        for z in node.bases:
            self.visit(z)
        for z in node.body:
            self.visit(z)
        for z in node.decorator_list:
            self.visit(z)
            
    def do_Continue(self,tree):
        pass

    def do_Delete(self,node):
        for z in node.targets:
            self.visit(z)

    def do_ExceptHandler(self,node):
        if node.type:
            self.visit(node.type)
        if node.name and isinstance(node.name,ast.Name):
            self.visit(node.name)
        for z in node.body:
            self.visit(z)

    def do_Exec(self,node):
        self.visit(node.body)
        if getattr(node,'globals',None):
            self.visit(node.globals)
        if getattr(node,'locals',None):
            self.visit(node.locals)

    def do_For (self,node):
        self.visit(node.target)
        self.visit(node.iter)
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)

    def do_FunctionDef (self,node):
        self.visit(node.args)
        for z in node.body:
            self.visit(z)
        for z in node.decorator_list:
            self.visit(z)

    def do_Global(self,node):
        pass

    def do_If(self,node):
        self.visit(node.test)
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)

    def do_Import(self,node):
        pass


    def do_ImportFrom(self,node):
        # for z in node.names:
            # self.visit(z)
        pass

    def do_Lambda(self,node):
        
        self.visit(node.args)
        self.visit(node.body)

    def do_Module (self,node):
        for z in node.body:
            self.visit(z)

    def do_Pass(self,node):
        pass

    def do_Print(self,node):
        if getattr(node,'dest',None):
            self.visit(node.dest)
        for expr in node.values:
            self.visit(expr)

    def do_Raise(self,node):
        if getattr(node,'type',None):
            self.visit(node.type)
        if getattr(node,'inst',None):
            self.visit(node.inst)
        if getattr(node,'tback',None):
            self.visit(node.tback)

    def do_Return(self,node):
        if node.value:
            self.visit(node.value)

    def do_Try(self,node):
        for z in node.body:
            self.visit(z)
        for z in node.handlers:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
        for z in node.finalbody:
            self.visit(z)

    def do_TryExcept(self,node):
        for z in node.body:
            self.visit(z)
        for z in node.handlers:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)

    def do_TryFinally(self,node):
        for z in node.body:
            self.visit(z)
        for z in node.finalbody:
            self.visit(z)

    def do_While (self,node):
        self.visit(node.test)
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
            
    def do_With (self,node):
        self.visit(node.context_expr)
        if node.optional_vars:
            self.visit(node.optional_vars)
        for z in node.body:
            self.visit(z)

    def do_Yield(self,node):
        if node.value:
            self.visit(node.value)

    def visit(self,node):
        '''Visit a *single* ast node.  Visitors are responsible for visiting children!'''
        assert isinstance(node,ast.AST),node.__class__.__name__
        method_name = 'do_' + node.__class__.__name__
        method = getattr(self,method_name)
        return method(node)