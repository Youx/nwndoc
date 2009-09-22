require 'rubygems'
require 'liquid'

require 'lib/albino'

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
      render_pygments(context, super.to_s)
    end

    def render_pygments(context, code)
      return "<notextile>" + Albino.new(code, @lang).to_s(@options) + "</notextile>"
    end
end


Liquid::Template.register_tag('highlight', HighlightBlock)
