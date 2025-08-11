module Jekyll
  class CategoryPageGenerator < Generator
    safe true
    priority :lowest

    def generate(site)
      return unless site.layouts.key? 'category'
      
      dir = site.config['category_dir'] || 'category'
      
      site.categories.each_key do |category|
        category_slug = category.downcase.gsub(/\s+/, '-').gsub(/[^\w-]/, '')
        
        site.pages << CategoryPage.new(site, site.source, File.join(dir, category_slug), category)
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