import os
import inspect
from pathlib import Path
import pandas as pd

def run_check(report_name, expected, actual, reporter=None, caller=None):
    if reporter is None:
        try:
            reporter = inspect.stack()[1].function
        except Exception as e:
            reporter = None
    
    if caller is None:
        try:
            py_path = Path(inspect.stack()[1].filename)
            caller = f'{py_path.parent.name}/{py_path.name}'
        except Exception as e:
            caller = None

    passed = actual == expected
    report = RunChecksReport(reporter=reporter, caller=caller)
    report.append(
        check_fn_name=report_name, 
        expected_val=expected, 
        actual_val=actual, 
        passed=passed
    )
    return report


class RunChecksReport:
    def __init__(self, reporter='<uknown>', caller='<uknown>'):
        self.check_fn_name = []
        self.expected_val = []
        self.actual_val = []
        self.passed = []
        self.reporter = []
        self.caller = []

        self._default_reporter = reporter
        self._default_caller = caller

        self._current_step = 0
        self._num_reports = 0

    def append(self, check_fn_name, expected_val, actual_val, passed, 
               reporter=None, caller=None):
        self.check_fn_name.append(check_fn_name)
        self.expected_val.append(expected_val)
        self.actual_val.append(actual_val)
        self.passed.append(passed)       
        self.reporter.append(reporter if reporter is not None else self._default_reporter)
        self.caller.append(caller if caller is not None else self._default_caller)

    def __repr__(self):
        return repr(self.passed)
    
    def __iadd__(self, other):
        if other is None:
            return self

        new_report = RunChecksReport()
        new_report.check_fn_name = self.check_fn_name + other.check_fn_name
        new_report.expected_val = self.expected_val + other.expected_val
        new_report.actual_val = self.actual_val + other.actual_val
        new_report.passed = self.passed + other.passed
        new_report.reporter = self.reporter + other.reporter
        new_report.caller = self.caller + other.caller
        return new_report
    
    def __iter__(self):
        self._current_step = 0
        self._num_reports = len(self.passed)
        return self

    def __next__(self):
        if self._current_step >= self._num_reports:
            raise StopIteration
                
        else:
            val = self.passed[self._current_step]
            self._current_step += 1
            return val
                 
    def to_pdf(self):
        return pd.DataFrame({
            'caller': self.caller,
            'reporter': self.reporter,
            'test-name': self.check_fn_name,
            'expected-value': self.expected_val,
            'actual-value': self.actual_val,
            'test-passed': self.passed,
        })

    def save_to(self, file_path):
        if not file_path:
            return
        
        if os.path.exists(file_path):
            results_df = pd.read_csv(file_path, sep=' ')
            results_df = pd.concat([results_df, self.to_pdf()])
        else:
            results_df = self.to_pdf()

        results_df.to_csv(file_path, sep=' ', index=False)

    def display(self):
        results_df = self.to_pdf()
        name_max_len = results_df['caller'].str.len().max() + 3
        # n_tests_recorded = results_df['caller'].nunique()
        max_checks = results_df['caller'].value_counts().max()
        ratio_str_max = len(f'{max_checks}/{max_checks}')
        
        try:
            term_width = os.get_terminal_size().columns - 1
        except OSError:
            term_width = 0
        
        for test_script, test_results_df in results_df.groupby('caller'):
            if len(test_results_df) == 0:
                continue
            
            name_len = len(test_script)
            dots_str = ''.join(['.']*(name_max_len - name_len))
            name_formated = f'{test_script}{dots_str}'
            
            failed_df = test_results_df[test_results_df['test-passed'] == False]
            n_tests = len(test_results_df)
            n_failed = len(failed_df)
            n_passed = n_tests - n_failed
            check_char = '\u2717' if n_failed > 0 else '\u2713'
            ratio_str =  f'{n_passed}/{n_tests}'
            ratio_padding = ' '*(ratio_str_max - len(ratio_str))
            
            print(f'{name_formated} {ratio_padding}{ratio_str} passed: {check_char}')
            for _, row in test_results_df.iterrows():
                if row['test-passed']:
                    row_str = f'  [PASSED] {row["reporter"]}::{row["test-name"]}()'
                else:
                    row_str = f'  [FAILED] {row["reporter"]}::{row["test-name"]}() [expected: \"{row["expected-value"]}\"; actual: {row["actual-value"]}]'

                row_len = len(row_str)
                if term_width and term_width > row_len:
                    row_str += '.'*(term_width - row_len - 1)
                row_str += '\u2713' if row['test-passed'] else '\u2717'
                print(row_str)
