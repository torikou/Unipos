import pandas as pd
import networkx as nx
import codecs
import matplotlib.pyplot as plt
from community import community_louvain

#グラフの大きさを決める
plt.figure(figsize = (20,20))
# メンバーのデータをデータフレーム化。read_csvを使わないのは日本語対応用
with codecs.open("member_path", "r", "Shift-JIS", "ignore") as file:
	df_name = pd.read_table(file, delimiter=",")
with codecs.open("data_path", "r", "Shift-JIS", "ignore") as file:
	df_ft = pd.read_table(file, delimiter=",")
	# 空のオブジェクトを用意
	g=nx.Graph()
	# 用意したグラフオブジェクトにノード(メンバー)を追加
	for i in range(len(df_name)):
		g.add_node(df_name.iloc[i,1])
	# 同じグループで活動しているメンバーについては、無条件で繋げる
	for i in range(len(df_name)):
		for j in range(len(df_name)):
			if df_name.iloc[i,4] == df_name.iloc[j,4] and i != j:
				g.add_edge(df_name.iloc[i,1], df_name.iloc[j,1], weight=1)
	# 投稿の送受信関係のあるメンバーについて、ノードを接続
	for i in range(len(df_ft)):
		if not g.has_node(df_ft.iloc[i,0]) or not g.has_node(df_ft.iloc[i,1]):
			continue
		#既存のエッジの場合weight+=1
		if g.has_edge(df_ft.iloc[i,0], df_ft.iloc[i,1]):
			#ver2.X以降g.edgeとすると怒られる模様
#			g.edge[df_ft.iloc[i,0]][df_ft.iloc[i,1]]["weight"] += 1
			g.adj[df_ft.iloc[i,0]][df_ft.iloc[i,1]]["weight"] += 1
		else:
			g.add_edge(df_ft.iloc[i,0], df_ft.iloc[i,1], weight=1)
	# 無向グラフ化。kで指定しているのはノード間の反発力
	pos = nx.spring_layout(g, k=0.3)
	# ノードのモジュラリティ最大化
	partition = community_louvain.best_partition(g)
	# 媒介中心性をベースにサイズを計算
	between_cent = nx.communicability_betweenness_centrality(g)
	node_size = [5000 * size for size in list(between_cent.values())]
	# 媒介中心性を上位からソートして表示
	for k in sorted(between_cent, key=lambda k:between_cent[k]):
		print(k, between_cent[k])
	# エッジのweightに応じてエッジを太くする
	edge_width = [ d["weight"]*0.2 for (u,v,d) in g.edges(data=True)]
	#表示
	nx.draw_networkx_nodes(g, pos,  node_color=[partition[node] for node in g.nodes()],alpha=0.6, node_size=node_size)
	nx.draw_networkx_labels(g, pos, fontsize=14, font_family="Osaka", font_weight="bold")
	nx.draw_networkx_edges(g, pos, alpha=0.4, edge_color="C", width=edge_width)
	plt.show()
