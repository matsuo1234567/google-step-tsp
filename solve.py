#!/usr/bin/env python3

import sys
import math
from common import print_tour, read_input

def distance(city1, city2):
    """2つの都市間のユークリッド距離を計算する"""
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)

def solve(cities):
    """
    複数の戦略を組み合わせて巡回セールスマン問題を解く
    1. 前処理: 孤立した点を先に処理する
    2. 構築: 凸包＋挿入法で質の高い初期ルートを作成する
    3. 改善: 2-opt法でルートを局所最適化し、交差を解消する
    """
    N = len(cities)
    if N == 0:
        return []

    # 全ての都市間の距離を事前に計算しておく
    dist_matrix = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(i, N):
            dist_matrix[i][j] = dist_matrix[j][i] = distance(cities[i], cities[j])

    # --- ステップ1: 孤立点の処理（前処理）---
    # 各点から最も近い点までの距離を計算
    nearest_dists = []
    for i in range(N):
        min_dist = float('inf')
        for j in range(N):
            if i == j: continue
            min_dist = min(min_dist, dist_matrix[i][j])
        nearest_dists.append(min_dist)
    
    # 平均の最近傍距離を計算し、それを基に孤立点の閾値を設定
    avg_nearest_dist = sum(nearest_dists) / N if N > 0 else 0
    # 平均の1.5倍以上離れている点を「孤立点」と見なす
    isolation_threshold = avg_nearest_dist * 1.5 
    
    isolated_indices = {i for i, d in enumerate(nearest_dists) if d > isolation_threshold}
    
    # 孤立点以外の点で初期ルートを構築する
    remaining_indices_for_hull = list(set(range(N)) - isolated_indices)
    
    if len(remaining_indices_for_hull) < 2:
        # ほとんどが孤立点の場合、単純な貪欲法で初期ルートを作る
        tour = list(range(N))
    else:
        # --- ステップ2: 凸包＋挿入法（構築） ---
        # 孤立点以外で凸包を形成
        # (この部分は簡略化し、残った点で挿入法を行う)
        tour = [remaining_indices_for_hull[0]]
        unvisited = set(remaining_indices_for_hull[1:])

        # 挿入法で孤立点以外の点をルートに追加
        while unvisited:
            best_insertion_cost = float('inf')
            best_point_to_insert = -1
            best_insertion_edge_index = -1
            
            for point_idx in unvisited:
                for i in range(len(tour)):
                    u_idx, v_idx = tour[i], tour[(i + 1) % len(tour)]
                    cost = dist_matrix[u_idx][point_idx] + dist_matrix[point_idx][v_idx] - dist_matrix[u_idx][v_idx]
                    if cost < best_insertion_cost:
                        best_insertion_cost = cost
                        best_point_to_insert = point_idx
                        best_insertion_edge_index = i
            
            tour.insert(best_insertion_edge_index + 1, best_point_to_insert)
            unvisited.remove(best_point_to_insert)

        # 最後に孤立点を挿入法で追加
        unvisited_isolated = isolated_indices
        while unvisited_isolated:
            best_insertion_cost = float('inf')
            best_point_to_insert = -1
            best_insertion_edge_index = -1

            for point_idx in unvisited_isolated:
                for i in range(len(tour)):
                    u_idx, v_idx = tour[i], tour[(i + 1) % len(tour)]
                    cost = dist_matrix[u_idx][point_idx] + dist_matrix[point_idx][v_idx] - dist_matrix[u_idx][v_idx]
                    if cost < best_insertion_cost:
                        best_insertion_cost = cost
                        best_point_to_insert = point_idx
                        best_insertion_edge_index = i

            tour.insert(best_insertion_edge_index + 1, best_point_to_insert)
            unvisited_isolated.remove(best_point_to_insert)

    # --- ステップ3: 2-opt法（改善） ---
    improved = True
    while improved:
        improved = False
        for i in range(N - 1):
            for j in range(i + 2, N):
                # ループの最後と最初をつなぐ辺も考慮
                i_plus_1 = (i + 1) % N
                j_plus_1 = (j + 1) % N
                
                # 辺(i, i+1)と辺(j, j+1)を辺(i, j)と辺(i+1, j+1)に繋ぎ変える
                current_dist = dist_matrix[tour[i]][tour[i_plus_1]] + dist_matrix[tour[j]][tour[j_plus_1]]
                new_dist = dist_matrix[tour[i]][tour[j]] + dist_matrix[tour[i_plus_1]][tour[j_plus_1]]

                if new_dist < current_dist:
                    # ルートを改善できるなら、i+1からjまでを逆順にする
                    sub_tour_to_reverse = tour[i_plus_1 : j + 1]
                    tour[i_plus_1 : j + 1] = sub_tour_to_reverse[::-1]
                    improved = True

    return tour

if __name__ == '__main__':
    assert len(sys.argv) > 1
    cities = read_input(sys.argv[1])
    tour = solve(cities)
    print_tour(tour)
