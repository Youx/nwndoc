#!/usr/bin/env ruby

require 'rubygems'
require 'yaml'
require 'fileutils'

# Included
require 'lib/highlight'
require 'lib/albino'

# Gems
require 'RedCloth'
require 'liquid'
require 'json'

start = Time.now

FileUtils.rm_r('output') if File.exists?('output')

tree = []
hftree = {}
search_data = {}

tree.push(["Functions","README.html","",[]])

search_data["badges"] = ["nwn"]

search_data["index"] = {}
search_data["index"]["searchIndex"] = []
search_data["index"]["longSearchIndex"] = []
search_data["index"]["info"] = []


ftemplate = Liquid::Template.parse(File.read(File.join('templates','functions.liquid')))
main_template = Liquid::Template.parse(File.read(File.join('templates','main.html')))
limit_parse = 9999
limit_curr = 0

Dir.open(File.join('src','Functions')).each do |filename|
	if filename =~ /\.yaml$/ && limit_curr < limit_parse
		print('.')
		function_info=YAML::load(File.open(File.join('src','Functions',filename)))
		
		search_data["index"]["searchIndex"].push(function_info['name'].downcase)
		search_data["index"]["longSearchIndex"].push(function_info['name'].downcase)
		search_data["index"]["info"].push(
				[ function_info['name'],
				function_info["seealso"]["categories"].join(' / '),
				"Functions/#{function_info['name']}.html",
				"",
				function_info['shortdesc'],
				1,0
				]
				)

		tree_el = [function_info["name"], "Functions/#{function_info['name']}.html","",[]]
		function_info['seealso']['categories'].each do |cat|
			if !hftree[cat]
				hftree[cat] = [cat, '', '', []] 
				tree[0][3].push(hftree[cat])
			end
			hftree[cat][3].push(tree_el)
		end

		redcloth = RedCloth.new(ftemplate.render('function' => function_info)).to_html
		Dir.mkdir('output') if ! File.exists?('output')
		Dir.mkdir(File.join('output','Functions')) if ! File.exists?(File.join('output','Functions'))
		File.open(File.join("output", 'Functions', filename.gsub('yaml','html')), "w") do |out|
			out.write(main_template.render('content' => redcloth, 'function' =>function_info))
		end
		limit_curr+=1
	end
end

puts('')

# Sort the tree
tree[0][3].sort! {|x,y| x[0] <=> y[0] }
#tree[0][3].each {|cat| cat.sort! {|x,y|
#	puts("#{x[0]} <=> #{y[0]}")
#	x[0] <=> y[0]}}

File.open(File.join('panel','search_index.js'),'w') do |f| f.write("var search_data = #{search_data.to_json};") end
File.open(File.join('panel','tree.js'),'w') do |f| f.write("var tree = #{tree.to_json};") end

# Copy additional files
FileUtils.cp_r('css', 'output/css')
FileUtils.cp_r('js', 'output/js')
FileUtils.cp_r('panel', 'output/panel')
FileUtils.cp_r('i', 'output/i')
FileUtils.cp(['index.html','README.html'],'output')
finish = Time.now
tdiff = finish - start
puts("Documentation compiled in #{tdiff} seconds")
