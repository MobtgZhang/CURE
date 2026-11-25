"""Reaggregate the frozen component and tool-development observations."""
from collections import Counter, defaultdict
from statistics import mean

from .io import read_csv, write_csv, write_json


def episode_matrix(rows, methods, task_count):
    matrix = defaultdict(dict)
    for row in rows:
        group = matrix[row['method']]
        assert row['task'] not in group, row
        assert (row['status'], row['match']) in {('scored', '0'), ('scored', '1'), ('unavailable', '')}, row
        group[row['task']] = row
    assert set(matrix) == set(methods)
    support = set(matrix[methods[0]])
    assert len(support) == task_count and all(set(group) == support for group in matrix.values())
    return matrix, sorted(support)


def aggregate(matrix, methods, support):
    summaries = []
    for method in methods:
        rows = [matrix[method][task] for task in support]
        summaries.append(dict(method=method, attempts=len(rows),
                              matches=sum(row['match'] == '1' for row in rows),
                              unavailable=sum(row['status'] == 'unavailable' for row in rows),
                              mean_reported_tokens=mean(int(row['reported_tokens']) for row in rows),
                              mean_calls=mean(int(row['calls']) for row in rows)))
    return summaries


def reconstruct(directory, output):
    component_methods = ('cure_l', 'no_ledger', 'no_challenge', 'target_only')
    episodes = read_csv(directory / 'component_episodes.csv')
    matrix, support = episode_matrix(episodes, component_methods, 30)
    common = [task for task in support if all(matrix[method][task]['status'] == 'scored' for method in component_methods)]
    component = aggregate(matrix, component_methods, common)
    assert len(common) == 27
    assert [row['matches'] for row in component] == [16, 15, 16, 16]
    assert [round(row['mean_reported_tokens'] / 1000, 1) for row in component] == [41.6, 40.7, 41.0, 26.4]
    for method in ('no_challenge', 'target_only'):
        assert all(matrix[method][task]['match'] == matrix['cure_l'][task]['match'] for task in common)
    target_savings = 1 - component[-1]['mean_reported_tokens'] / component[0]['mean_reported_tokens']
    assert round(100 * target_savings, 1) == 36.6
    write_csv(output / 'component_summary.csv', component)

    pilot_methods = ('tool_agent', 'fineverify', 'deepverifier', 'cure')
    development_methods = (*pilot_methods, 'prior_workflow')
    episodes = read_csv(directory / 'tool_development_episodes.csv')
    matrix, support = episode_matrix(episodes, development_methods, 40)
    development = aggregate(matrix, development_methods, support)
    assert [row['matches'] for row in development] == [26, 24, 25, 25, 26]
    assert [row['unavailable'] for row in development] == [0, 1, 0, 8, 4]
    assert [round(row['mean_reported_tokens'] / 1000, 1) for row in development] == [30.1, 152.5, 108.2, 121.4, 127.3]
    development_ratio = development[3]['mean_reported_tokens'] / development[0]['mean_reported_tokens']
    assert round(development_ratio, 2) == 4.04
    write_csv(output / 'tool_development_summary.csv', development)

    details = read_csv(directory / 'tool_cure_details.csv')
    assert len(details) == 40 and {row['task'] for row in details} == set(support)
    assert all(row['status'] == matrix['cure'][row['task']]['status'] for row in details)
    scored = [row for row in details if row['status'] == 'scored']
    failures = dict(Counter(row['failure_type'] for row in details if row['status'] == 'unavailable'))
    assert failures == {'BudgetError': 6, 'ValueError': 2}
    assert all(row['final_match'] == matrix['cure'][row['task']]['match'] == row['replay_match'] for row in scored)
    stages = {stage: sum(int(row[f'{stage}_match']) for row in scored) for stage in ('draft', 'checker', 'final')}
    synthesized = sum(row['final_match'] == '1' and row['draft_match'] == row['checker_match'] == '0' for row in scored)
    replay_matches = sum(int(row['replay_match']) for row in details)
    reviewed_ledgers = sum(row['review_status'] == 'reviewed_conditions' for row in details)
    conditions = {field: sum(int(row[field]) for row in details) for field in ('reviewed', 'new', 'established', 'unresolved')}
    assert list(stages.values()) == [23, 24, 25] and synthesized == 2 and replay_matches == 27
    assert reviewed_ledgers == 39 and list(conditions.values()) == [149, 44, 49, 56]

    episodes = read_csv(directory / 'tool_pilot_episodes.csv')
    matrix, support = episode_matrix(episodes, pilot_methods, 24)
    pilot = aggregate(matrix, pilot_methods, support)
    assert all(row['matches'] == 17 and row['unavailable'] == 0 for row in pilot)
    assert all(len({matrix[method][task]['match'] for method in pilot_methods}) == 1 for task in support)
    for row in pilot:
        labels = [matrix[row['method']][task]['mismatch_at_accepted_stop'] for task in support]
        row['mismatches_at_accepted_stop'] = sum(int(label) for label in labels if label) if any(labels) else None
    assert [row['mismatches_at_accepted_stop'] for row in pilot] == [None, 3, 7, None]
    pilot_ratio = pilot[-1]['mean_reported_tokens'] / pilot[0]['mean_reported_tokens']
    assert round(pilot_ratio, 2) == 3.51
    write_csv(output / 'tool_pilot_summary.csv', pilot)

    summary = dict(component_common=len(common), target_token_savings=target_savings,
                   development_token_ratio=development_ratio, development_failures=failures,
                   development_stage_matches=stages, development_final_only_matches=synthesized,
                   development_replay_matches=replay_matches, reviewed_ledgers=reviewed_ledgers,
                   development_conditions=conditions, pilot_token_ratio=pilot_ratio)
    write_json(output / 'supplementary_studies.json', summary)
    return summary
