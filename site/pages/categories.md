---
layout: default
title: "Categories"
permalink: /categories/
---

<div class="categories-index">
  <header class="page-header">
    <h1 class="page-title">All Categories</h1>
    <p class="page-subtitle">Browse posts by category</p>
  </header>

  <div class="category-grid">
    {% assign categories = site.categories | sort %}
    {% for category in categories %}
      <div class="category-item card">
        <div class="category-header">
          <h3 class="category-name">{{ category[0] | replace: '_', ' ' | replace: '-', ' ' | capitalize }}</h3>
          <span class="post-count">{{ category[1] | size }} post{% if category[1].size != 1 %}s{% endif %}</span>
        </div>
        
        <div class="recent-posts">
          {% for post in category[1] limit:3 %}
            <div class="post-preview">
              <a href="{{ post.url | relative_url }}" class="post-link">{{ post.title }}</a>
              <time class="post-date">{{ post.date | date: "%b %d, %Y" }}</time>
            </div>
          {% endfor %}
        </div>
        
        <a href="{{ '/category/' | append: category[0] | replace: '_', '-' | replace: ' ', '-' | downcase | relative_url }}" class="view-all">
          View all posts in {{ category[0] | replace: '_', ' ' | replace: '-', ' ' | capitalize }}
        </a>
      </div>
    {% endfor %}
  </div>
</div>

<style>
#content .categories-index { padding: 18px 0; }
#content .page-header { margin-bottom: 32px; text-align: center; }
#content .page-title { font-size: var(--fs-4); margin: 0 0 8px; }
#content .page-subtitle { color: var(--text-muted); margin: 0; }

#content .category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

#content .category-item {
  padding: 24px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
  background: var(--surface);
}

#content .category-item:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary);
}

#content .category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

#content .category-name {
  margin: 0;
  font-size: var(--fs-2);
  font-weight: 600;
  color: var(--text);
}

#content .post-count {
  background: var(--muted-surface);
  color: var(--text-muted);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: var(--fs-0);
  font-weight: 500;
}

#content .recent-posts {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

#content .post-preview {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

#content .post-link {
  color: var(--text);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  line-height: 1.3;
}

#content .post-link:hover {
  color: var(--primary);
  text-decoration: underline;
  text-underline-offset: 2px;
}

#content .post-date {
  color: var(--text-muted);
  font-size: var(--fs-0);
}

#content .view-all {
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: gap 0.2s ease;
}

#content .view-all:hover {
  text-decoration: underline;
  text-underline-offset: 2px;
  gap: 8px;
}

@media (max-width: 640px) {
  #content .category-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  #content .category-item {
    padding: 20px;
  }
  
  #content .category-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>