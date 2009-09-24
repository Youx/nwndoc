#!/usr/bin/env ruby

require 'rubygems'
require 'yaml'
require 'fileutils'

# Included
require 'lib/highlight'
#require 'lib/albino'

# Gems
require 'RedCloth'
require 'liquid'
require 'json'

# Change this to output to a different directory
PREFIX_DIR = 'output'

# Directory containing templates - do not change
TEMPLATE_DIR = 'templates'

# The sources for the YAML and files we copy
SRC_YAML = FileList['src/Functions/*.yaml','src/Constants/*.yaml']
SRC_COPY = FileList['index.html','panel/index.html','js/*.js','css/*.css','i/*.png','README.html']

# The outputs from the YAML and files we copy
OUT_HTML = SRC_YAML.collect{|x| x.sub('src',PREFIX_DIR).ext('html')}
OUT_COPY = SRC_COPY.collect{|x| File.join(PREFIX_DIR, x)}
SEARCH_INDEX_JS = File.join('output','panel','search_index.js')
TREE_JS = File.join('output','panel','tree.js')

# Load the templates only once
TEMPLATES = {
  :functions => [
    Liquid::Template.parse(File.read(File.join(TEMPLATE_DIR, 'functions.liquid'))),
    Liquid::Template.parse(File.read(File.join(TEMPLATE_DIR, 'functions.html')))],
  :constants => [
    Liquid::Template.parse(File.read(File.join(TEMPLATE_DIR, 'constants.liquid'))),
    Liquid::Template.parse(File.read(File.join(TEMPLATE_DIR, 'constants.html')))]
}

directory PREFIX_DIR
directory File.join(PREFIX_DIR, 'Functions')
directory File.join(PREFIX_DIR, 'Constants')
directory File.join(PREFIX_DIR, 'panel')
directory File.join(PREFIX_DIR, 'css')
directory File.join(PREFIX_DIR, 'js')
directory File.join(PREFIX_DIR, 'i')

# For each type of doc, we have a class with the same name
# as the directory
class Functions
  def Functions.searchIndex(data)
    return [data['name'].downcase]
  end
  
  def Functions.longSearchIndex(data)
    return [data['name'].downcase]
  end
  
  def Functions.info(data)
    return [[ data['name'], data["seealso"]["categories"].join(' / '), 
      "Functions/#{data['name']}.html", "", data['shortdesc'], 1,0]]
  end
  
  def Functions.tree_els(data)
    return [[data['name'], "Functions/#{data['name']}.html","",[]]]
  end
	
  def Functions.tree_parents(data)
    return data['seealso']['categories'].collect do |c|
      [c, "", "", []]
    end
  end
  
  def Functions.tree_base()
    return ["Functions","README.html","",[]]
  end
  
  def Functions.generate(src, out)
    file out => [File.join(PREFIX_DIR, 'Functions'), src] do
      File.open(src) do |f|
        data=YAML::load(f)
        render1 = TEMPLATES[:functions][0].render('function' => data)
        redcloth = RedCloth.new(render1).to_html
      	render2 = TEMPLATES[:functions][1].render('content' => redcloth, 'function' => data)
      	File.open(out,'w') do |o|
      		o.write(render2)
      	end
      end
    end
  end
end

class Constants
  def Constants.searchIndex(data)
    return data['constants'].collect do |c|
      c['name'].downcase
    end
  end
  
  def Constants.longSearchIndex(data)
    return data['constants'].collect do |c|
      c['name'].downcase
    end
  end
  
  def Constants.info(data)
    return data['constants'].collect do |c|
      [c['name'], data['category'], "Constants/#{data['category'].gsub('*','.html')}", '', c['shortdesc'], 1, 0]
    end
  end
  
  def Constants.tree_els(data)
    return data['constants'].collect do |c|
      [c["name"], "Constants/#{data['category'].gsub('*','.html')}","",[]]
    end
	end  
  
  def Constants.tree_parents(data)
    return [[data['category'], "Constants/#{data['category'].gsub('*','.html')}", "", []]]
  end
  
  def Constants.tree_base()
    return ["Constants","README.html","",[]]
  end
  
  def Constants.generate(src, out)
    file out => [File.join(PREFIX_DIR, 'Constants'), src] do
      File.open(src) do |f|
        data=YAML::load(f)
        render1 = TEMPLATES[:constants][0].render('constants' => data)
        redcloth = RedCloth.new(render1).to_html
  	  	render2 = TEMPLATES[:constants][1].render('content' => redcloth, 'title' => File.basename(src,'yaml'))
  	  	File.open(out,'w') do |o|
  	  		o.write(render2)
  	  	end
  	  end
  	end
  end
end

# Instructions on how to generate output/panel/search_index.js
file SEARCH_INDEX_JS => [File.join(PREFIX_DIR,'panel'), SRC_YAML].flatten do
  search_data = {}
  search_data['badges'] = ['nwn']
  search_data['index'] = {}
  search_data['index']['searchIndex'] = []
  search_data['index']['longSearchIndex'] = []
  search_data['index']['info'] = []
  
  SRC_YAML.each do |src|
    File.open(src) do |f|
      data=YAML::load(f)
      cat = File.basename(File.dirname(src))

      my_class = Object.const_get(cat)
      search_data['index']['searchIndex'].concat(my_class.searchIndex(data))
      search_data['index']['longSearchIndex'].concat(my_class.longSearchIndex(data))
      search_data['index']['info'].concat(my_class.info(data))
    end
  end
  File.open(SEARCH_INDEX_JS,'w') do |f|
    f.write("var search_data = #{search_data.to_json};")
  end
end

# Instructions on how to generate output/panel/tree.js
file TREE_JS => [File.join(PREFIX_DIR,'panel'), SRC_YAML].flatten do
  tree = []
  SRC_YAML.each do |src|
    File.open(src) do |f|
      data=YAML::load(f)
      cat = File.basename(File.dirname(src))
      my_class = Object.const_get(cat)

      # If the tree root (ex : "Functions", "Constants", ...)
      # does not exist, we create it
      tree_root = tree.find {|x| x[0] == cat}
      if !tree_root
        tree_root = my_class.tree_base()
        tree.push(tree_root)
      end

      my_class.tree_parents(data).each do |parent|
        tree_cat = tree_root[3].find {|x| x[0] == parent[0]}
        if !tree_cat
          tree_cat = parent
          tree_root[3].push(tree_cat)
        end
        tree_cat[3].concat(my_class.tree_els(data))
      end
    end
  end
  # Sort the first two level
  tree.sort! {|x,y| x[0] <=> y[0]}
  tree.each {|el| el[3].sort! {|x,y| x[0] <=> y[0]}}
  File.open(TREE_JS,'w') do |f|
    f.write("var tree = #{tree.to_json};")
  end
end

# Generate all the jobs for YAML -> HTML
SRC_YAML.each do |srcfile|
  outfile = srcfile.gsub('src',PREFIX_DIR).ext('html')
  cat = File.basename(File.dirname(srcfile))
  my_class = Object.const_get(cat)
  my_class.generate(srcfile, outfile)
end
# Generate all copy jobs
SRC_COPY.each do |srcfile|
  outfile = File.join(PREFIX_DIR, srcfile)
  parent_dir = File.dirname(outfile)
  file outfile => [parent_dir, srcfile] do
    FileUtils.cp(srcfile, outfile)
  end
end


#multitask :generate_yaml => OUT_HTML

task :default => [PREFIX_DIR, OUT_COPY, SEARCH_INDEX_JS, TREE_JS, OUT_HTML].flatten
