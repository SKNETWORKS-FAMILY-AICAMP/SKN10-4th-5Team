import random
import pandas as pd
from datetime import datetime
from math import factorial
import itertools

class TeamManager:
    def __init__(self, students, team_leaders):
        self.students = students
        self.team_leaders = team_leaders
        self.team_count = 5
        self._restrictions = set()  # private 변수로 변경
        self.remaining_students = [s for s in students if s not in team_leaders]
        self.combinations = []
        self.saved_combinations = []
        self.total_combinations = self.calculate_total_combinations()
        self.generate_combinations()
    
    def calculate_total_combinations(self):
        """실제 가능한 조합 수 계산 (제한 사항 고려)"""
        # 팀장을 제외한 나머지 학생 수로 계산
        n = len(self.remaining_students)
        base_team_size = n // self.team_count
        remainder = n % self.team_count
        
        # 각 팀의 크기 계산
        team_sizes = [base_team_size + (1 if i < remainder else 0) 
                     for i in range(self.team_count)]
        
        # 기본 조합 수 계산
        total = factorial(n)
        for size in team_sizes:
            total //= factorial(size)
            
        # 제한 사항이 있는 경우 조합 수 감소
        if self._restrictions:
            # 제한당 약 10%씩 감소 (근사치)
            reduction_factor = 0.9 ** len(self._restrictions)
            total = int(total * reduction_factor)
        
        return max(1, total)  # 최소 1개 보장
    
    def get_restrictions(self):
        """현재 설정된 제한 목록 반환"""
        return list(self._restrictions)  # set을 list로 변환하여 반환
    
    def add_restriction(self, student1, student2):
        """특정 학생들이 같은 팀이 되지 않도록 제한"""
        if student1 not in self.students or student2 not in self.students:
            return False
            
        if (student1, student2) not in self._restrictions and \
           (student2, student1) not in self._restrictions:
            self._restrictions.add((student1, student2))
            # 제한 추가 후 전체 조합 수 재계산
            self.total_combinations = self.calculate_total_combinations()
            # 조합 재생성
            self.generate_combinations()
            return True
        return False
    
    def remove_restriction(self, student1, student2):
        """제한 조건 제거"""
        if (student1, student2) in self._restrictions:
            self._restrictions.remove((student1, student2))
        elif (student2, student1) in self._restrictions:
            self._restrictions.remove((student2, student1))
        else:
            return False
        
        # 제한 제거 후 전체 조합 수 재계산
        self.total_combinations = self.calculate_total_combinations()
        # 조합 재생성
        self.generate_combinations()
        return True
    
    def check_restrictions(self, teams):
        """제한 조건 확인"""
        for student1, student2 in self._restrictions:
            for team in teams:
                if student1 in team and student2 in team:
                    return False
        return True
    
    def check_team_leader_rule(self, teams):
        """각 팀에 최소 한 명의 팀장이 있는지 확인"""
        for team in teams:
            has_leader = False
            for member in team:
                if member in self.team_leaders:
                    has_leader = True
                    break
            if not has_leader:
                return False
        return True
    
    def generate_combinations(self):
        """조합 생성 (제한 사항 고려)"""
        self.combinations = []
        attempts = 0
        max_attempts = min(self.total_combinations, 1000)  # 최대 1000개로 제한
        
        while len(self.combinations) < max_attempts and attempts < max_attempts * 2:
            # 팀장이 고정된 팀 생성
            teams = [[leader] for leader in self.team_leaders]
            
            # 나머지 학생들을 랜덤하게 배정
            current_students = self.remaining_students.copy()
            random.shuffle(current_students)
            
            # 팀별 추가 인원 수 계산
            base_size = len(current_students) // self.team_count
            remainder = len(current_students) % self.team_count
            
            # 각 팀에 학생 배정
            valid_combination = True
            current_idx = 0
            
            for team_idx in range(self.team_count):
                additional_members = base_size + (1 if team_idx < remainder else 0)
                team_members = current_students[current_idx:current_idx + additional_members]
                
                # 제한 조건 확인
                for member in team_members:
                    for existing_member in teams[team_idx]:
                        if (member, existing_member) in self._restrictions or \
                           (existing_member, member) in self._restrictions:
                            valid_combination = False
                            break
                    if not valid_combination:
                        break
                
                if not valid_combination:
                    break
                
                teams[team_idx].extend(team_members)
                current_idx += additional_members
            
            if valid_combination and not any(self.is_same_combination(teams, existing) 
                                           for existing in self.combinations):
                self.combinations.append(teams)
            
            attempts += 1
    
    def is_same_combination(self, teams1, teams2):
        """두 팀 조합이 동일한지 확인"""
        return sorted(map(tuple, teams1)) == sorted(map(tuple, teams2))
    
    def get_team_combination(self, index):
        if not 0 <= index < len(self.combinations):
            return None
        return self.combinations[index]
    
    def save_combination(self, index):
        """현재 조합 저장"""
        if 0 <= index < len(self.combinations):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            saved_combo = {
                'timestamp': timestamp,
                'teams': self.combinations[index]
            }
            self.saved_combinations.append(saved_combo)
            return True
        return False
    
    def export_to_excel(self, index, filename=None):
        """팀 조합을 엑셀 파일로 내보내기"""
        if not 0 <= index < len(self.combinations):
            return False
            
        teams = self.combinations[index]
        max_members = max(len(team) for team in teams)
        
        # DataFrame 생성을 위한 데이터 준비
        data = {}
        for i, team in enumerate(teams, 1):
            # 팀원 수가 다른 경우를 위해 빈 값으로 채우기
            team_data = team + [''] * (max_members - len(team))
            data[f'{i}팀'] = team_data
            
        df = pd.DataFrame(data)
        
        if filename is None:
            filename = f'team_combination_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        df.to_excel(filename, index=False)
        return filename 