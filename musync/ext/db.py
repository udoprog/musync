from musync.goals import Goal
from musync.custom import md5sum

class DatabaseGoal(Goal):
    ns = "db";

class AddGoal(DatabaseGoal):
    prefix = "md5"
    fileonly = True;
    
    def run_file(self, source):
        self.printer.notice(repr(md5sum(source.path)) + ":", source.path);
