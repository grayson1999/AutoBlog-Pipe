module Jekyll
  class CategoryPageGenerator < Generator
    safe true
    priority :lowest

    def generate(site)
      return unless site.layouts.key? 'category'
      
      dir = site.config['category_dir'] || 'category'
      
      site.categories.each_key do |category|
        # Create pages for both underscore and hyphen versions
        category_underscore = category.downcase.gsub(/\s+/, '_').gsub(/[^\w_]/, '')
        category_hyphen = category.downcase.gsub(/[\s_]+/, '-').gsub(/[^\w-]/, '')
        
        # Create underscore version (for existing URLs)
        site.pages << CategoryPage.new(site, site.source, File.join(dir, category_underscore), category)
        
        # Create hyphen version (for new URLs) if different
        if category_underscore != category_hyphen
          site.pages << CategoryPage.new(site, site.source, File.join(dir, category_hyphen), category)
        end
      end
    end
  end

  class CategoryPage < Page
    def initialize(site, base, dir, category)
      @site = site
      @base = base
      @dir = dir
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(base, '_layouts'), 'category.html')
      self.data['category'] = category
      self.data['title'] = "Category: #{category}"
      self.data['description'] = "Posts in #{category} category"
    end
  end
end