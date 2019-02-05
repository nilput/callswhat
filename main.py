import pygraphviz #dependency

import sys
import os
import os.path
import subprocess as ps
import shutil
import argparse

'''
input: directory
output: graph

how?
for each .c file run gendot command

'''

def find_by_label(graph, label):
	for node in graph.iternodes():
		if 'label' not in node.attr:
			continue
		if node.attr['label'].find(label) != -1:
			return node
	return None

def find_c_sources(dir):
	files = []
	with os.scandir(dir) as it:
		for entry in it:
			if entry.is_dir():
				l = find_c_sources(entry.path)
				files.extend(l)
			elif entry.is_file() and entry.path.endswith('.c'):
				files.append(entry.path)
	return files

dot_graph_list = []

def outify(path, ext):
	if not os.path.exists('outtmp'):
		os.mkdir('outtmp')
	name = os.path.basename(path)
	return os.path.join('outtmp', name + ext)

#returns a list of dots
def process_sources(sources):
	dots = []
	for source_path in sources:
		outllvm = outify(source_path, '.lv')
		completed = ps.run(args=['clang', '-S', '-emit-llvm', source_path, '-o',
							outllvm])
		completed.check_returncode() #raiess
		completed = ps.run(args=['opt', '-analyze', '-std-link-opts', '-dot-callgraph', outllvm])
		completed.check_returncode() #raiess
		assert(os.path.exists('callgraph.dot'))
		outdot = outify(source_path, '.dot')
		shutil.move('callgraph.dot', outdot)
		dots.append(outdot)
	return dots




class cfunc:
	def __init__(self, name, registry):
		self.name = name
		self.callees_set = set()
		self.called_by_set = set()
		self.registry = registry
	def called_by(self, other):
		self.called_by_set.add(other)
	def calls(self, other):
		self.callees_set.add(other)
		self.registry.get_or_insert(other).called_by(self.name)

class registry:
	def __init__(self):
		self.dict = {}
	def get_or_insert(self, name):
		if name not in self.dict:
			self.dict[name] = cfunc(name, self)
		return self.dict[name]
	def iter_func_to_callees(self):
		for func in self.dict.values():
			yield (func.name, tuple(func.callees_set))


def try_get_label(graph, node_name):
	node = graph.get_node(node_name)
	return node.attr['label']

#returns graph
def process_dots(dots):
	reg = registry()
	for dot_file in dots:
		grph = pygraphviz.AGraph()
		with open(dot_file,'r') as f:
			grph.from_string(f.read())
		for edge in grph.edges():
			src,dest = edge[0], edge[1]
			#print(dot_file, edge)
			srcn, destn = try_get_label(grph, src), try_get_label(grph, dest)
			if (srcn and destn):
				#print(srcn, 'calls', destn)
				reg.get_or_insert(srcn).calls(destn)
			elif srcn or destn:
				srcn = srcn if srcn else '?'
				destn = destn if destn else '?'
				print('warning, unknown name for function call {} -> {}'.format(srcn, destn))
	ngraph = pygraphviz.AGraph(directed=True)
	for func_name, calls in reg.iter_func_to_callees():
		if func_name.find('external node') != -1:
			continue #hardcoded :)
		ngraph.add_node(func_name, label=func_name)
		for callee in calls:
			ngraph.add_edge(func_name, callee)
	return ngraph





def graph_stuff(dotfile):
	file = dotfile
	grph = pygraphviz.AGraph()

	with open(file,'r') as f:
		grph.from_string(f.read())

	main_nd = find_by_label(grph, 'main')
	grph.add_node('test', label='test node')
	grph.add_edge('test', main_nd)
	
	grph.draw(os.path.basename(file)+'.png', prog='dot')
	grph.write(os.path.basename(file)+'.out.dot')


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', help='input directory')
	parser.add_argument('-o', help='output dotfile')
	args = parser.parse_args()
	if not args.d:
		print('error no input dir')
		return
	if not args.o:
		print('error no output file')
		return
	source_dir = args.d
	sources = find_c_sources(source_dir)
	dots = process_sources(sources)
	#print(*sources, sep='\n')
	#print()
	#print(*dots, sep='\n')
	print()
	G = process_dots(dots)
	G.write(args.o)
	G.draw(args.o+'.png',prog='dot')

	print('generated', args.o, args.o + '.png')




if __name__ == '__main__':
	main()