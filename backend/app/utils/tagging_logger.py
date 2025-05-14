import logging

class TaggingLogger:
    def __init__(self):
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
        self.errors = []

    def log_processed(self, status: str, error_message: str = None):
        self.stats['total_processed'] += 1
        if status == 'success':
            self.stats['successful'] += 1
        elif status == 'error':
            self.stats['failed'] += 1
            if error_message:
                self.errors.append(error_message)
        elif status == 'skipped':
            self.stats['skipped'] += 1

    def print_summary(self):
        print("\n----- Tagging Summary -----")
        print(f"Total Processed: {self.stats['total_processed']}")
        print(f"Successful     : {self.stats['successful']}")
        print(f"Failed         : {self.stats['failed']}")
        print(f"Skipped        : {self.stats['skipped']}")
        if self.errors:
            print("Errors:")
            for err in self.errors:
                print(f"  - {err}")
        print("-----------------------------\n") 