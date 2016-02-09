from collections import defaultdict

class Pipe(object):
    '''
    Base class for generating a pipe for a pipeline
    '''
    pipeline_pipes = defaultdict(dict)

    @classmethod
    def register_pipe(cls, cls2, pipeline_name):
        Pipe.pipeline_pipes[pipeline_name][cls2.__name__]=cls2

    @classmethod
    def get_pipes(cls, pipeline_name):
        '''
        Returns the dictionary of valid pipes classes in a pipeline by name
        '''
        return Pipe.pipeline_pipes[pipeline_name]

    @staticmethod
    def check_config(config):
        '''
        Implement this method to check that the input data is valid. It should
        be as strict as possible. By default, config is checked to be empty.
        '''
        pass

    @staticmethod
    def execute(data, config):
        '''
        Executes the pipe. Should return a PipeReturnValue. "data" is the value
        that one pipe passes to the other, and config is the specific config of
        a pipe.
        '''
        pass