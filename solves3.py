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
    2. 構築: 挿入法で質の高い初期ルートを作成する
    3. 改善: 3-opt法でルートを局所最適化し、より複雑な交差を解消する
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
    nearest_dists = [min(dist_matrix[i][j] for j in range(N) if i != j) if N > 1 else 0 for i in range(N)]
    avg_nearest_dist = sum(nearest_dists) / N if N > 0 else 0
    isolation_threshold = avg_nearest_dist * 1.5 
    isolated_indices = {i for i, d in enumerate(nearest_dists) if d > isolation_threshold}
    remaining_indices = list(set(range(N)) - isolated_indices)
    
    if not remaining_indices:
        remaining_indices = list(range(N))
        isolated_indices = set()
    
    # --- ステップ2: 挿入法（構築） ---
    tour = [remaining_indices[0]]
    unvisited = set(remaining_indices[1:])
    
    # 挿入法で孤立点以外の点をルートに追加
    while unvisited:
        best_cost, best_point, best_edge_idx = float('inf'), -1, -1
        for point_idx in unvisited:
            for i in range(len(tour)):
                u, v = tour[i], tour[(i + 1) % len(tour)]
                cost = dist_matrix[u][point_idx] + dist_matrix[point_idx][v] - dist_matrix[u][v]
                if cost < best_cost: best_cost, best_point, best_edge_idx = cost, point_idx, i
        tour.insert(best_edge_idx + 1, best_point)
        unvisited.remove(best_point)

    # 最後に孤立点を挿入法で追加
    while isolated_indices:
        best_cost, best_point, best_edge_idx = float('inf'), -1, -1
        for point_idx in isolated_indices:
            for i in range(len(tour)):
                u, v = tour[i], tour[(i + 1) % len(tour)]
                cost = dist_matrix[u][point_idx] + dist_matrix[point_idx][v] - dist_matrix[u][v]
                if cost < best_cost: best_cost, best_point, best_edge_idx = cost, point_idx, i
        tour.insert(best_edge_idx + 1, best_point)
        isolated_indices.remove(best_point)

    # --- ステップ3: 3-opt法（改善） ---
    # 注意: この処理は O(N^3) のため、Nが大きいと非常に時間がかかります。
improved = True
    while improved:
        improved = False
        # 3つの「辺」を選ぶ。辺は (tour[i], tour[i+1]) のように定義される
        for i in range(N):
            for j in range(i + 2, N):
                for k in range(j + 2, N + (1 if i > 0 else 0)):
                    # ループの終端を考慮 (i=0のときはkがN-1まで)
                    if k >= N : continue

                    # 辺(i, i+1), (j, j+1), (k, k+1) を切断する
                    # インデックスがNを超える場合は %N で巡回させる
                    A, B = tour[i], tour[(i + 1) % N]
                    C, D = tour[j], tour[(j + 1) % N]
                    E, F = tour[k], tour[(k + 1) % N]

                    # 8通りの繋ぎ変えパターンを試し、最も良いものを探す
                    # d0が現在のコスト
                    d0 = dist_matrix[A][B] + dist_matrix[C][D] + dist_matrix[E][F]
                    
                    # 2-optの繋ぎ変えパターン
                    d1 = dist_matrix[A][C] + dist_matrix[B][D] + dist_matrix[E][F] # (A,C),(B,D)
                    d2 = dist_matrix[A][B] + dist_matrix[C][E] + dist_matrix[D][F] # (C,E),(D,F)
                    d3 = dist_matrix[A][E] + dist_matrix[F][B] + dist_matrix[C][D] # (A,E),(F,B)
                    
                    # 3-optの繋ぎ変えパターン
                    d4 = dist_matrix[A][C] + dist_matrix[B][E] + dist_matrix[D][F]
                    d5 = dist_matrix[A][D] + dist_matrix[E][B] + dist_matrix[C][F]
                    d6 = dist_matrix[A][D] + dist_matrix[E][C] + dist_matrix[B][F]
                    d7 = dist_matrix[A][E] + dist_matrix[F][C] + dist_matrix[B][D]

                    # 最もコストが低い繋ぎ変えを探す
                    best_dist = min(d0, d1, d2, d3, d4, d5, d6, d7)

                    if best_dist < d0:
                        # 改善が見つかった場合、安全な方法でルートを更新
                        # セグメントを定義 (i+1からjまで、j+1からkまで)
                        # tourを直接スライスで書き換えるのではなく、部分を逆順にする
                        s1 = tour[i+1 : j+1]
                        s2 = tour[j+1 : k+1]
                        
                        new_tour = tour[:i+1]

                        if best_dist == d1: # 2-opt: i+1..j を反転
                            new_tour.extend(s1[::-1])
                            new_tour.extend(s2)
                        elif best_dist == d2: # 2-opt: j+1..k を反転
                            new_tour.extend(s1)
                            new_tour.extend(s2[::-1])
                        elif best_dist == d3: # 2-opt: i+1..k を反転
                            new_tour.extend((s1+s2)[::-1])
                        elif best_dist == d4: # 3-opt
                            new_tour.extend(s1[::-1])
                            new_tour.extend(s2[::-1])
                        elif best_dist == d5: # 3-opt
                            new_tour.extend(s2)
                            new_tour.extend(s1)
                        elif best_dist == d6: # 3-opt
                            new_tour.extend(s2[::-1])
                            new_tour.extend(s1)
                        elif best_dist == d7: # 3-opt
                            new_tour.extend(s2)
                            new_tour.extend(s1[::-1])
                        
                        # tourの末尾（k+1以降）を追加
                        new_tour.extend(tour[k+1:])
                        tour = new_tour
                        
                        improved = True
                        break # 改善したので内側のループから抜ける
                if improved: break
            if improved: break

    return tour

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使い方: python solve.py <input_file.csv>")
        sys.exit(1)
    
    input_filename = sys.argv[1]
    # 入力ファイル名から出力ファイル名を自動的に生成します。
    # 例: `input_6.csv` が入力なら `output_6.csv` が出力されます。
    output_filename = input_filename.replace('input_', 'output_')

    print(f"都市データを {input_filename} から読み込んでいます...")
    cities = read_input(input_filename)
    
    print("TSP問題を解いています... (Nが大きい場合、時間がかかります)")
    tour = solve(cities)
    
    # 指定されたフォーマットで出力ファイルに書き込みます。
    print(f"解を {output_filename} に書き込んでいます...")
    with open(output_filename, 'w') as f:
        f.write('index\n')
        for city_index in tour:
            f.write(f'{city_index}\n')
            
    print("完了しました。")
