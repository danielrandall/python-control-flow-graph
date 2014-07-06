'''
Creates a control flow graph (cfg)
'''

from src.traversers.astfulltraverser import AstFullTraverser
import ast
from pprint import pprint

class Block():
    ''' A basic control flow block.

    It has one entry point and several possible exit points.
    Note that the next_block is not necessarily an exit.
    '''
    
    # Block tags
    NORMAL = 0
    LOOP_HEADER = 1

    def __init__(self):
        # The next block along the function
        self.next_block = None
        self.has_return = False
        # Holds the statements in this block
        self.start_line_no = 0
        self.statements = []
        self.exit_blocks = []
        # Use to indicate whether the block has been visited. Used for printing
        self.marked = False
        # Used to describe special blocks
        self.tag = Block.NORMAL
        # Block which have been absorbed into this one
        self.dependents = []
        
    def copy_dict(self, copy_to):
        ''' Keep the name bindings but copy the class instances.
            Both bindings now point to the same variables.
            This function is used to simulate C pointers.
            TODO: Find a more elegant way of achieving this. '''
        for dependent in self.dependents:
            dependent.__dict__ = copy_to.__dict__
        self.__dict__ = copy_to.__dict__
        copy_to.dependents = self.dependents + [self]
        
# These are frame blocks.
# Idea for these are from PyPy
F_BLOCK_LOOP = 0
F_BLOCK_EXCEPT = 1
F_BLOCK_FINALLY = 2
F_BLOCK_FINALLY_END = 3

class ControlFlowGraph(AstFullTraverser):
    
    def __init__(self):
        self.current_block = None
        # Used to hold how control flow is nested (e.g. if inside of a for)
        self.frame_blocks = []
        self.current_line_num = 0
        
    def parse_ast(self, source_ast):
        self.run(source_ast)
        return source_ast
        
    def parse_file(self, file_path):
        source_ast = self.file_to_ast(file_path)
        return self.parse_ast(source_ast)
        
    def file_to_ast(self, file_path):
        s = self.get_source(file_path)
        return ast.parse(s, filename = file_path, mode = 'exec')
    
    def get_source(self, fn):
        ''' Return the entire contents of the file whose name is given.
            Almost most entirely copied from stc. '''
        try:
            f = open(fn,'r')
            s = f.read()
            f.close()
            return s
        except IOError:
            return ''
        
    def push_frame_block(self, kind, block):
        self.frame_blocks.append((kind, block))

    def pop_frame_block(self, kind, block):
        actual_kind, old_block = self.frame_blocks.pop()
        assert actual_kind == kind and old_block is block, \
            "mismatched frame blocks"
            
    def is_empty_block(self, candidate_block):
        return not candidate_block.statements
            
    def check_child_exits(self, candidate_block, after_control_block):
        ''' After if and loop blocks an after_if/loop block is created. If the
            if/loop blocks are the last in a straight line block of statements
            then the after blocks will be empty. All body/then/else exits will
            point to this block. If it is empty then swap for the given block.
            If it is not then set that block's exit as the given block. '''
        if candidate_block.has_return:
            # If the block has a return exit then can not be given another here
            return
        if self.is_empty_block(candidate_block):
            # candidate_block and after_control_block now point to the same
            # variables. They are now the same instance.
            candidate_block.copy_dict(after_control_block)
            return
        # This is needed to avoid two "Exits" appearing for the return or yield
        # at the end of a function.
        if not after_control_block in candidate_block.exit_blocks:
            candidate_block.exit_blocks.append(after_control_block)
            
    def add_to_block(self, node):
        ''' We want every try statement to be in its own block. '''
        if not self.current_block:
            return
        # We only want the 'top level' statements
        if self.current_line_num >= node.lineno:
            return   
        # Special cases - test must be in its own block
        if isinstance(node, ast.While) or isinstance(node, ast.For):
            if not self.is_empty_block(self.current_block):
                test_block = self.new_block()
                self.current_block.exit_blocks.append(test_block)
                self.use_next_block(test_block)
        self.current_line_num = node.lineno
        for f_block_type, f_block in reversed(self.frame_blocks):
            if f_block_type == F_BLOCK_EXCEPT:
                # Statement is in a try - set exits to next statement and
                # excepts
                self.current_block.statements.append(node)
                for handler in f_block:
                    self.current_block.exit_blocks.append(handler)
                # Special case
                if isinstance(node, ast.While) or isinstance(node, ast.For):
                    break
                next_statement_block = self.new_block()
                self.current_block.exit_blocks.append(next_statement_block)
                self.use_next_block(next_statement_block)
                break
        else:
            self.current_block.statements.append(node)
    
    def run(self, root):
        self.visit(root)
        
    def new_block(self):
        ''' From pypy. '''
        return Block()

    def use_block(self, block):
        ''' From pypy. '''
        self.current_block = block
        
    def empty_block(self, block):
        return not block.statements

    def use_next_block(self, block=None):
        """Set this block as the next_block for the last and use it.
           From pypy """
        if block is None:
            block = self.new_block()
        self.current_block.next_block = block
        self.use_block(block)
        return block
    
    def add_to_exits(self, source, dest):
        source.exit_blocks.append(dest)
        
    def visit(self, node):
        '''Visit a single node. Callers are responsible for visiting children.'''
        if self.check_has_return():
            return
        self.check_block_num(node)
        self.add_to_block(node)
        method = getattr(self, 'do_' + node.__class__.__name__)
        return method(node)

    def check_block_num(self, node):
        ''' Used for display purposes only. Each block is labelled with the
            line number of the the first statement in the block. '''
        if not self.current_block:
            return
        if not self.current_block.start_line_no:
            self.current_block.start_line_no = node.lineno
            print(self.current_block.start_line_no )
            
    def check_has_return(self):
        return self.current_block and self.current_block.has_return
    
    def do_FunctionDef(self, node):
        block = self.new_block()
        self.use_block(block)
        node.initial_block = block
        self.exit_block = self.new_block()
        # Special case
        self.exit_block.start_line_no = "Exit"
        for z in node.body:
            self.visit(z)
        # Here there's a chance that the last block already points the exit.
        # Such as yields and returns
        for e in self.current_block.exit_blocks:
            if e.start_line_no == "Exit":
                return
        else:
            self.check_child_exits(self.current_block, self.exit_block)
            
    def do_If(self, node):
        ''' If an if statement is the last in a straight line then an empty
            and unused block will be created as the after_if. '''
        if_block = self.current_block
        after_if_block = self.new_block()
        # Then block
        then_block = self.new_block()
        self.add_to_exits(if_block, then_block)
        self.use_block(then_block)
        for z in node.body:
            self.visit(z)
        # Make sure the then exits point to the correct place
        self.check_child_exits(self.current_block, after_if_block)
        # Else block
        if node.orelse:
            else_block = self.new_block()
            self.add_to_exits(if_block, else_block)
            self.use_block(else_block)
            for z in node.orelse:
                self.visit(z)
            # Make sure the else exits point to the correct place
            self.check_child_exits(self.current_block, after_if_block)
        else:
            self.add_to_exits(if_block, after_if_block)
        # Set the next block of the if to the after_if block
        if_block.next = after_if_block
        self.use_block(after_if_block)
        
    def do_While(self, node):
        self.do_Loop(node)
        
    def do_For(self, node):
        self.do_Loop(node)
        
    def do_Loop(self, node):
        ''' For and While loops are treated the same. The only difference is
            the possibility of iterators in a For loop.
            The loop body always returns to test unless there is a break or
            return.
            The else body is entered when the test is false but not when there
            is a break or an exception.
            The next block of the test could in theory be the else or after.
            But when we access it for the breaks we want it to be the after. '''
        # Put the test in its own block
        test_block = self.current_block
            
        test_block.tag = Block.LOOP_HEADER
        self.push_frame_block(F_BLOCK_LOOP, test_block)

        after_loop_block = self.new_block()
        loop_body_block = self.new_block()
        self.add_to_exits(test_block, loop_body_block)
        test_block.next = after_loop_block
        self.use_block(loop_body_block)
        for z in node.body:
            self.visit(z)
        self.check_child_exits(self.current_block, test_block)
        self.pop_frame_block(F_BLOCK_LOOP, test_block)
        
        if node.orelse:
            else_body = self.new_block()
            self.add_to_exits(test_block, else_body)
            self.use_block(else_body)
            else_body.next = after_loop_block
            for z in node.orelse:
                self.visit(z)
            self.check_child_exits(self.current_block, after_loop_block)
        else:
            self.add_to_exits(test_block, after_loop_block)
        
        self.use_next_block(after_loop_block)
        
    def do_Return(self, node):
        ''' End the current block here.
            No statements in this block after this are valid.
            In a try, returns go to the finally block. '''
        if node.value:
            self.visit(node.value)
        # Check if the block is an try-finally.
        for f_block_type, f_block in reversed(self.frame_blocks):
            if f_block_type == F_BLOCK_FINALLY:
                return_exit = f_block
                break
        else:
            return_exit = self.exit_block
        self.current_block.exit_blocks.append(return_exit)
        self.current_block.has_return = True
        
    def do_Continue(self, node):
        ''' Continues can not be in a finally block.
            TODO: Fix this up.  '''
        if not self.frame_blocks:
            self.error("'continue' not properly in loop", node)
        current_block, block = self.frame_blocks[-1]
        if current_block == F_BLOCK_LOOP:
            self.current_block.exit_blocks.append(block)
        elif current_block == F_BLOCK_EXCEPT or \
                current_block == F_BLOCK_FINALLY:
            # Find the loop
            for i in range(len(self.frame_blocks) - 2, -1, -1):
                f_type, block = self.frame_blocks[i]
                if f_type == F_BLOCK_LOOP:
                    self.current_block.exit_blocks.append(block)
                    break
                if f_type == F_BLOCK_FINALLY_END:
                    self.error("'continue' not supported inside 'finally' "
                                   "clause", node)
            else:
                self.error("'continue' not properly in loop", node)
                return
        elif current_block == F_BLOCK_FINALLY_END:
            self.error("'continue' not supported inside 'finally' clause", node)
        self.current_block.has_return = True
    
    def do_Break(self, node):
        ''' A break can only be in a loop.
            A break causes the current block to exit to block after the loop
            header (its next) '''
        # Find first loop in stack
        for f_block_type, f_block in reversed(self.frame_blocks):
            if f_block_type == F_BLOCK_LOOP:
                self.current_block.exit_blocks.append(f_block.next)
                break
        else:
            self.error("'break' outside loop", node)
        self.current_block.has_return = True
        
    def do_Yield(self, node):
        ''' Here we deal with the control flow when the iterator goes through
            the function.
            We don't set has_return to true since, in theory, it can either
            exit or continue from here. '''
        self.current_block.exit_blocks.append(self.exit_block)
        next_block = self.new_block()
        self.current_block.exit_blocks.append(next_block)
        self.use_next_block(next_block)
        
    def do_Try(self, node):
        ''' It is a great ordeal to find out which statements can cause which
            exceptions. Assume every statement can cause any exception. So
            each statement has its own block and a link to each exception.
            
            orelse executed if an exception is not raised therefore last try
            statement should point to the else.
            
            nested try-finallys go to each other during a return 
            TODO'''
        after_try_block = self.new_block()
        final_block = None
        try_body_block = self.new_block()
        self.current_block.next_block = try_body_block
        orelse_block = self.new_block()
        
        before_line_no = self.current_line_num
        if node.finalbody:
            # Either end of orelse or try should point to finally body
            final_block = self.new_block()
            self.use_block(final_block)
            self.push_frame_block(F_BLOCK_FINALLY_END, node)
            for z in node.finalbody:
                self.visit(z)
            self.pop_frame_block(F_BLOCK_FINALLY_END, node)
            self.check_child_exits(self.current_block, after_try_block)
        self.current_line_num = before_line_no
        
        before_line_no = self.current_line_num
        exception_handlers = []
        for handler in node.handlers:
            assert isinstance(handler, ast.ExceptHandler)
            initial_handler_block = self.new_block()
            self.use_block(initial_handler_block)
            for z in handler.body:
                self.visit(z)
            handler_exit = final_block if node.finalbody else after_try_block
            self.check_child_exits(self.current_block, handler_exit)
            exception_handlers.append(initial_handler_block)   
        self.current_line_num = before_line_no         
        
        f_blocks = []
        if node.finalbody:
            f_blocks.append((F_BLOCK_FINALLY, final_block))
        if node.handlers:
            f_blocks.append((F_BLOCK_EXCEPT, exception_handlers))
        for f in f_blocks:
            self.push_frame_block(f[0], f[1])
        self.use_block(try_body_block)
        for z in node.body:
            self.visit(z)
        for f in reversed(f_blocks):
            self.pop_frame_block(f[0], f[1])
        
        if node.orelse:
            orelse_block = self.new_block()
            # Last block in body can always go to the orelse
            self.check_child_exits(self.current_block, orelse_block)
            self.use_block(orelse_block)
            for z in node.orelse:
                self.visit(z)
            orelse_exit = final_block if node.finalbody else after_try_block
            self.check_child_exits(self.current_block, orelse_exit)
        else:
            self.check_child_exits(self.current_block, after_try_block)
            
        self.use_next_block(after_try_block)     
        
class PrintCFG(AstFullTraverser):
    
    def __init__(self, cfg):
        self.run(cfg)
        
    def run(self, node):
        self.visit(node)
        
    def visit(self, node):
        '''Visit a single node. Callers are responsible for visiting children.'''
        method = getattr(self, 'do_' + node.__class__.__name__)
        return method(node)
    
    def do_FunctionDef(self, node):
        print ("CFG for " + node.name)
        self.process_blocks(node.initial_block)
        
    def process_blocks(self, block):
        ''' TODO: Handle infinite loops '''
        if block.marked:
            return
        if block.start_line_no == "Exit":
            return
        exit_nos = [block.start_line_no for block in block.exit_blocks]
        pprint("Block starting at: " + str(block.start_line_no) + " to " + str(exit_nos))
        block.marked = True
        for an_exit in block.exit_blocks:
            self.process_blocks(an_exit)
        if block.next_block:
            self.process_blocks(block.next_block)
        
        
if __name__ == '__main__':
    fn = "/homes/dr1810/4thYear/individualProject/pythonTypes/testFiles/test.py"
    cfg = ControlFlowGraph()
    s_ast = cfg.parse_file(fn)
    PrintCFG(s_ast)
    
        
        
        
    