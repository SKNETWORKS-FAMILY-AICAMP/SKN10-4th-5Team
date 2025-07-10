# 최적화: 통합 CSV 기반 팀 구성 프로그램
import pandas as pd
from ortools.sat.python import cp_model
import io
import pandas as pd

def run_team_optimization(csv_content, optimize_for="balanced", use_project_preference=False, 
                        custom_weights=None):
    """CSV 내용을 직접 받아 팀 최적화를 실행하고 결과를 콘솔에 출력"""
    print("📂 CSV 데이터 처리 중...")
    print(f"최적화 모드: {optimize_for}")
    print(f"프로젝트 선호도 사용: {use_project_preference}")
    
    # ===== 데이터 불러오기 =====
    data = pd.read_csv(io.StringIO(csv_content))
    student_names = data['name'].tolist()
    skills = data['skill_score'].tolist()
    name_to_index = {name: i for i, name in enumerate(student_names)}
    index_to_name = {i: name for name, i in name_to_index.items()}

    NUM_STUDENTS = len(student_names)
    NUM_TEAMS = 5
    NUM_PROJECTS = 5
    MAX_SOLUTIONS = 1000
    OPTIMIZE_FOR = optimize_for
    USE_PROJECT_PREFERENCE = use_project_preference

    # 프로젝트 선호도 데이터 로드
    project_prefs = data[[f'{i}지망' for i in range(1, 5)]].values.tolist()

    # ===== 관계 설정 =====
    def parse(cell):
        if pd.isna(cell): return []
        return [x.strip() for x in str(cell).split(',') if x.strip()]

    # 이전 팀원 관계 데이터 로드
    teamed_with = {row['name']: parse(row.get('teamed_with', '')) 
                   for _, row in data.iterrows()}
    
    # 이전 팀원 관계를 인덱스로 변환
    previous_teammates = [(name_to_index[a], name_to_index[b]) 
                         for a, bs in teamed_with.items() 
                         for b in bs if a in name_to_index and b in name_to_index]

    custom_want_with = {row['name']: parse(row.get('want_with', '')) for _, row in data.iterrows()}
    custom_avoid_with = {row['name']: parse(row.get('avoid_with', '')) for _, row in data.iterrows()}
    custom_must_with = {row['name']: parse(row.get('must_with', '')) for _, row in data.iterrows()}

    want_with = [(name_to_index[a], name_to_index[b]) 
                 for a, bs in custom_want_with.items() 
                 for b in bs if a in name_to_index and b in name_to_index]
    avoid_with = [(name_to_index[a], name_to_index[b]) 
                  for a, bs in custom_avoid_with.items() 
                  for b in bs if a in name_to_index and b in name_to_index]
    must_with = [(name_to_index[a], name_to_index[b]) 
                 for a, bs in custom_must_with.items() 
                 for b in bs if a in name_to_index and b in name_to_index]

    # ===== 모델 정의 =====
    model = cp_model.CpModel()
    team_vars = [model.NewIntVar(0, NUM_TEAMS - 1, f'team_{i}') for i in range(NUM_STUDENTS)]

    for a, b in avoid_with:
        model.Add(team_vars[a] != team_vars[b])
    for a, b in must_with:
        model.Add(team_vars[a] == team_vars[b])

    # ===== 희망 팀 소프트 제약 =====
    soft_constraints = []
    for a, b in want_with:
        same_team = model.NewBoolVar(f'want_{a}_{b}')
        model.Add(team_vars[a] == team_vars[b]).OnlyEnforceIf(same_team)
        model.Add(team_vars[a] != team_vars[b]).OnlyEnforceIf(same_team.Not())
        soft_constraints.append(same_team)

    # ===== 팀별 실력 제약 =====
    team_skills = [model.NewIntVar(0, sum(skills), f'team_skill_{t}') for t in range(NUM_TEAMS)]
    for t in range(NUM_TEAMS):
        members = [model.NewBoolVar(f'm_{i}_t{t}') for i in range(NUM_STUDENTS)]
        for i in range(NUM_STUDENTS):
            model.Add(team_vars[i] == t).OnlyEnforceIf(members[i])
            model.Add(team_vars[i] != t).OnlyEnforceIf(members[i].Not())
        team_size = sum(members)
        model.Add(team_size >= 5)
        model.Add(team_size <= 6)
        model.Add(team_skills[t] == sum(members[i] * skills[i] for i in range(NUM_STUDENTS)))

    # ===== 실력 편차 최소화 =====
    avg_team_skill = sum(skills) // NUM_TEAMS
    abs_diff_vars = []
    for t in range(NUM_TEAMS):
        diff_var = model.NewIntVar(-sum(skills), sum(skills), f'diff_team_{t}')
        abs_diff = model.NewIntVar(0, sum(skills), f'abs_diff_team_{t}')
        model.Add(diff_var == team_skills[t] - avg_team_skill)
        model.AddAbsEquality(abs_diff, diff_var)
        abs_diff_vars.append(abs_diff)
    
    total_abs_deviation = model.NewIntVar(0, sum(skills) * NUM_TEAMS, 'total_abs_deviation')
    model.Add(total_abs_deviation == sum(abs_diff_vars))

    # ===== 프로젝트 선호도 점수 계산 =====
    if USE_PROJECT_PREFERENCE:
        team_project = [model.NewIntVar(0, NUM_PROJECTS - 1, f'team_proj_{t}') for t in range(NUM_TEAMS)]
        project_scores = []
        for i in range(NUM_STUDENTS):
            for t in range(NUM_TEAMS):
                is_in_team = model.NewBoolVar(f'in_team_{i}_{t}')
                model.Add(team_vars[i] == t).OnlyEnforceIf(is_in_team)
                model.Add(team_vars[i] != t).OnlyEnforceIf(is_in_team.Not())
                for p in range(NUM_PROJECTS):
                    is_proj = model.NewBoolVar(f'team{t}_is_proj{p}')
                    model.Add(team_project[t] == p).OnlyEnforceIf(is_proj)
                    model.Add(team_project[t] != p).OnlyEnforceIf(is_proj.Not())
                    score = 0
                    if p in project_prefs[i]:
                        rank = project_prefs[i].index(p)
                        score = 4 - rank
                    contrib = model.NewIntVar(0, 4, f'pref_score_{i}_{t}_{p}')
                    model.Add(contrib == score).OnlyEnforceIf([is_in_team, is_proj])
                    model.Add(contrib == 0).OnlyEnforceIf(is_in_team.Not())
                    project_scores.append(contrib)
        project_satisfaction = model.NewIntVar(0, NUM_STUDENTS * 4, 'project_satisfaction')
        model.Add(project_satisfaction == sum(project_scores))
        model.AddAllDifferent(team_project)

    # 이전 팀원과 다른 팀이 되도록 하는 소프트 제약 추가
    new_teammate_constraints = []
    for a, b in previous_teammates:
        different_team = model.NewBoolVar(f'different_{a}_{b}')
        model.Add(team_vars[a] != team_vars[b]).OnlyEnforceIf(different_team)
        model.Add(team_vars[a] == team_vars[b]).OnlyEnforceIf(different_team.Not())
        new_teammate_constraints.append(different_team)
    
    # ===== 목적 함수 설정 =====
    # 기본 가중치 설정
    weights = {
        'skillWeight': 2.0,
        'preferenceWeight': 1.0,
        'previousTeamWeight': 1.0,
        'projectWeight': 1.0
    }

    # 사용자 정의 가중치가 있으면 적용
    if custom_weights:
        weights.update(custom_weights)

    # 목적 함수 설정
    objective_terms = [
        (total_abs_deviation, float(weights['skillWeight'])),
        (sum(soft_constraints), -float(weights['preferenceWeight'])),
        (sum(new_teammate_constraints), float(weights['previousTeamWeight']))
    ]
    
    if USE_PROJECT_PREFERENCE:
        objective_terms.append(
            (project_satisfaction, -float(weights['projectWeight']))
        )
    
    model.Minimize(sum(term * weight for term, weight in objective_terms))

    # ===== 솔루션 수집 =====
    class SolutionCollector(cp_model.CpSolverSolutionCallback):
        def __init__(self, team_vars, soft_constraints, new_teammate_constraints, max_solutions):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.team_vars = team_vars
            self.soft_constraints = soft_constraints
            self.new_teammate_constraints = new_teammate_constraints
            self.max_solutions = max_solutions
            self.solutions = []
            self.scores = []
            self.solution_count = 0
            self.team_projects = []  # 프로젝트 배정 결과 저장

        def on_solution_callback(self):
            if self.solution_count < self.max_solutions:
                assignment = [self.Value(v) for v in self.team_vars]
                score = sum(self.Value(c) for c in self.soft_constraints)
                
                # 프로젝트 배정 결과 저장
                if USE_PROJECT_PREFERENCE:
                    projects = [self.Value(p) for p in team_project]
                    self.team_projects.append(projects)
                else:
                    self.team_projects.append(None)
                
                if USE_PROJECT_PREFERENCE:
                    score += self.Value(project_satisfaction)
                previous_teammate_penalty = sum(self.Value(c) for c in self.new_teammate_constraints)
                score -= previous_teammate_penalty
                self.solutions.append(assignment)
                self.scores.append(score)
            self.solution_count += 1

    collector = SolutionCollector(team_vars, soft_constraints, new_teammate_constraints, MAX_SOLUTIONS)
    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = True
    solver.parameters.max_time_in_seconds = 60
    
    print("🔍 솔루션 탐색 중...")
    status = solver.Solve(model, collector)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("\n✨ 최적화 완료!")
        # max_score 계산
        max_score = len(soft_constraints)
        if USE_PROJECT_PREFERENCE:
            max_score += NUM_STUDENTS * 4

        sorted_results = sorted(zip(collector.solutions, collector.scores), 
                              key=lambda x: x[1], reverse=True)[:10]
        
        for idx, (assignment, score) in enumerate(sorted_results):
            percent_score = round(100 * score / max_score, 2)
            print(f"\n✅ 조합 {idx + 1} (수강생 만족도: {score} / {max_score} = {percent_score}%)")
            teams = [[] for _ in range(NUM_TEAMS)]
            for i, team in enumerate(assignment):
                teams[team].append(student_names[i])
            
            for t, members in enumerate(teams):
                print(f"  🟦 팀 {t + 1}: {', '.join(members)}")
                avg_skill = round(sum(skills[student_names.index(name)] for name in members) / len(members), 2)
                print(f"     🔧 평균 실력: {avg_skill}")
                if USE_PROJECT_PREFERENCE and collector.team_projects[idx] is not None:
                    print(f"     📌 배정된 프로젝트: 프로젝트 {collector.team_projects[idx][t] + 1}")
        
        return sorted_results, max_score, collector.team_projects  # team_projects 추가
    else:
        print("❌ 유효한 해결책을 찾을 수 없습니다.")
        return None, 0, None  # team_projects도 None으로 반환

if __name__ == "__main__":
    # 테스트용 CSV 파일 경로
    test_csv_path = Path(__file__).parent / 'data' / 'students.csv'
    if test_csv_path.exists():
        run_team_optimization(test_csv_path)
    else:
        print(f"❌ CSV 파일을 찾을 수 없습니다: {test_csv_path}")
