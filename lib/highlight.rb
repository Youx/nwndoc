require 'rubygems'
require 'coderay'
require 'liquid'

require 'lib/nwnlexer.rb'

class HighlightBlock < Liquid::Block
    include Liquid::StandardFilters

    # we need a language, but the linenos argument is optional.
    SYNTAX = /(\w+)\s?(:?linenos)?\s?/

    def initialize(tag_name, markup, tokens)
      super
      if markup =~ SYNTAX
        @lang = $1
        if defined? $2
          # additional options to pass to Albino.
          @options = { 'O' => 'linenos=inline' }
        else
          @options = {}
        end
      else
        raise SyntaxError.new("Syntax Error in 'highlight' - Valid syntax: highlight <lang> [linenos]")
      end
    end

    def render(context)
      render_coderay(context, super.to_s)
    end

    def render_coderay(context, code)
      return "<notextile>" + CodeRay.scan(code, :nwn).div(:css => :class) + "</notextile>"
    end
end


Liquid::Template.register_tag('highlight', HighlightBlock)
