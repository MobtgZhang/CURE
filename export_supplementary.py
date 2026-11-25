#!/usr/bin/env python3
"""Project the three supplementary studies from locally held ICDE records."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from cure_audit.io import digest, read_csv, read_jsonl, write_csv, write_json


def export(source, destination):
    inputs = set()

    def read_records(name):
        path = source / name
        inputs.add(path)
        return read_jsonl(path) if path.suffix == '.jsonl' else read_csv(path)

    def episodes(study, methods):
        records = []
        for method in methods:
            for path in sorted((source / study).glob(f'*/{method}/*/episode.json')):
                inputs.add(path)
                records.append((json.loads(path.read_text()), path.parent.name))
        return records

    def project(records, prefix):
        ids = {task: f'{prefix}{index:03}' for index, task in enumerate(
            sorted({record['task_id'] for record, _ in records}), start=1)}
        rows = [dict(task=ids[record['task_id']], method=record['method'],
                     status=record['status'], match=record['success'] if record['status'] == 'scored' else '',
                     reported_tokens=record['usage']['total_tokens'], calls=len(record['calls']))
                for record, _ in records]
        rows.sort(key=lambda row: (row['task'], row['method']))
        return rows, ids

    variants = ('no_ledger', 'no_challenge', 'target_only')
    component = episodes('next_revision/test', variants)
    support = {row['task_id'] for row, _ in component}
    component.extend((row, anchor) for row, anchor in episodes('next_revision/test', ('cure_l',))
                     if row['task_id'] in support)
    component_rows, _ = project(component, 'C')
    write_csv(destination / 'component_episodes.csv', component_rows)

    arms = ('tool_agent', 'fineverify', 'deepverifier', 'cure')
    development = episodes('recovery_input_development/development', (*arms, 'prior_workflow'))
    development_rows, development_ids = project(development, 'D')
    write_csv(destination / 'tool_development_episodes.csv', development_rows)
    by_anchor = {anchor: development_ids[row['task_id']] for row, anchor in development if row['method'] == 'cure'}
    failure = read_records('recovery_input_development/analysis/failure_audit_20261108/questions.jsonl')
    review = read_records('recovery_input_development/analysis/source_alignment/review_outcome_questions.jsonl')
    replay = read_records('completion_policy_development_replay/questions.jsonl')

    def index(rows):
        return {by_anchor[row['episode']]: row for row in rows}

    review_by_task = index(review)
    replay_by_task = index(replay)
    details = []
    for task, failure_row in sorted(index(failure).items()):
        review_row = review_by_task[task]
        replay_row = replay_by_task[task]
        details.append(dict(task=task, status=failure_row['status'], failure_type=failure_row['error_type'],
                            draft_match=review_row['draft_correct'], checker_match=review_row['checker_correct'],
                            final_match=review_row['final_correct'], replay_match=replay_row['success'],
                            review_status=review_row['review_status'], reviewed=review_row['reviewed_conditions'],
                            new=review_row['newly_resolved_conditions'], established=review_row['already_established_conditions'],
                            unresolved=review_row['unresolved_conditions']))
    write_csv(destination / 'tool_cure_details.csv', details)

    pilot = episodes('common_evidence_development/development', arms)
    pilot_rows, pilot_ids = project(pilot, 'P')
    coverage = read_records('common_evidence_development/analysis/candidate_coverage.csv')
    stops = {(pilot_ids[row['task_id']], row['method']): row['strict_mismatch_at_accepted_stop'] for row in coverage}
    for row in pilot_rows:
        row['mismatch_at_accepted_stop'] = stops[row['task'], row['method']]
    write_csv(destination / 'tool_pilot_episodes.csv', pilot_rows)
    write_json(destination / 'supplementary_source_hashes.json', sorted(digest(path) for path in inputs))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original_outputs', type=Path, help='Original code/outputs/icde2027 directory')
    parser.add_argument('destination', type=Path, help='Directory for projected CSVs')
    options = parser.parse_args()
    export(options.original_outputs, options.destination)
