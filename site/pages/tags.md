---
layout: default
title: "Tags"
permalink: /tags/
---

<div class="tags-index">
  <header class="page-header">
    <h1 class="page-title">All Tags</h1>
    <p class="page-subtitle">Browse posts by tag</p>
  </header>

  <div class="tag-cloud">
    {% assign tags = site.tags | sort %}
    {% for tag in tags %}
      <a href="#{{ tag[0] | slugify }}" class="tag-item" data-tag="{{ tag[0] }}">
        {{ tag[0] }}
        <span class="count">{{ tag[1] | size }}</span>
      </a>
    {% endfor %}
  </div>

  <div class="posts-by-tag">
    {% for tag in site.tags %}
      <section class="tag-section" id="{{ tag[0] | slugify }}" data-tag="{{ tag[0] }}">
        <h2 class="tag-title">{{ tag[0] }}</h2>
        <p class="tag-count">{{ tag[1] | size }} post{% if tag[1].size != 1 %}s{% endif %}</p>
        
        <div class="posts-grid">
          {% assign posts = tag[1] | sort: 'date' | reverse %}
          {% for post in posts %}
            <article class="post-card card">
              <div class="post-meta">
                <time datetime="{{ post.date | date_to_xmlschema }}">
                  {{ post.date | date: "%b %d, %Y" }}
                </time>
                {% if post.categories.first %}
                  <span class="post-category">{{ post.categories.first | replace: '_', ' ' | replace: '-', ' ' | capitalize }}</span>
                {% endif %}
              </div>
              
              <h3 class="post-title">
                <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
              </h3>
              
              {% if post.excerpt %}
                <p class="post-excerpt">{{ post.excerpt | strip_html | truncatewords: 20 }}</p>
              {% endif %}
              
              <a href="{{ post.url | relative_url }}" class="read-more">Read More</a>
            </article>
          {% endfor %}
        </div>
      </section>
    {% endfor %}
  </div>
</div>

<style>
#content .tags-index { padding: 18px 0; }
#content .page-header { margin-bottom: 32px; text-align: center; }
#content .page-title { font-size: var(--fs-4); margin: 0 0 8px; }
#content .page-subtitle { color: var(--text-muted); margin: 0; }

#content .tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 48px;
  justify-content: center;
}

#content .tag-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--muted-surface);
  border: 1px solid var(--border);
  border-radius: 24px;
  text-decoration: none;
  color: var(--text-muted);
  font-weight: 500;
  transition: all 0.2s ease;
}

#content .tag-item:hover,
#content .tag-item.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

#content .tag-item .count {
  background: rgba(255,255,255,0.2);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: var(--fs-0);
  font-weight: 600;
}

#content .tag-item:hover .count,
#content .tag-item.active .count {
  background: rgba(255,255,255,0.3);
}

#content .posts-by-tag {
  display: none;
}

#content .posts-by-tag.show {
  display: block;
}

#content .tag-section {
  display: none;
  margin-bottom: 48px;
}

#content .tag-section.active {
  display: block;
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

#content .tag-title {
  font-size: var(--fs-3);
  margin: 0 0 4px;
  color: var(--text);
}

#content .tag-count {
  color: var(--text-muted);
  margin: 0 0 24px;
  font-size: var(--fs-0);
}

#content .posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

#content .post-card {
  padding: 20px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
  background: var(--surface);
}

#content .post-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary);
}

#content .post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: var(--fs-0);
}

#content .post-meta time {
  color: var(--text-muted);
  font-weight: 500;
}

#content .post-category {
  background: var(--primary);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: var(--fs-0);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

#content .post-title {
  margin: 0 0 12px;
}

#content .post-title a {
  color: var(--text);
  text-decoration: none;
  font-size: var(--fs-2);
  font-weight: 600;
  line-height: 1.3;
  transition: color 0.2s;
}

#content .post-title a:hover {
  color: var(--primary);
}

#content .post-excerpt {
  color: var(--text-muted);
  line-height: 1.5;
  margin-bottom: 16px;
}

#content .read-more {
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: gap 0.2s ease;
}

#content .read-more:hover {
  text-decoration: underline;
  text-underline-offset: 2px;
  gap: 8px;
}

@media (max-width: 640px) {
  #content .posts-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  #content .post-card {
    padding: 16px;
  }
  
  #content .post-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  #content .tag-cloud {
    gap: 8px;
  }
  
  #content .tag-item {
    padding: 6px 12px;
    font-size: var(--fs-0);
  }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
  const tagItems = document.querySelectorAll('.tag-item');
  const tagSections = document.querySelectorAll('.tag-section');
  const postsContainer = document.querySelector('.posts-by-tag');
  
  function showTag(targetTag) {
    // Hide all sections
    tagSections.forEach(section => {
      section.classList.remove('active');
    });
    
    // Remove active class from all tag items
    tagItems.forEach(item => {
      item.classList.remove('active');
    });
    
    // Show target section
    const targetSection = document.getElementById(targetTag);
    if (targetSection) {
      targetSection.classList.add('active');
      postsContainer.classList.add('show');
    }
    
    // Add active class to clicked tag
    const activeTagItem = document.querySelector(`[data-tag="${targetTag.replace('-', ' ')}"]`);
    if (activeTagItem) {
      activeTagItem.classList.add('active');
    }
  }
  
  // Handle tag clicks
  tagItems.forEach(item => {
    item.addEventListener('click', function(e) {
      e.preventDefault();
      const tag = this.getAttribute('data-tag');
      const tagSlug = tag.toLowerCase().replace(/\s+/g, '-');
      showTag(tagSlug);
      
      // Update URL hash
      history.pushState(null, null, `#${tagSlug}`);
    });
  });
  
  // Handle initial hash
  if (window.location.hash) {
    const hash = window.location.hash.substring(1);
    showTag(hash);
  }
  
  // Handle back/forward buttons
  window.addEventListener('popstate', function() {
    if (window.location.hash) {
      const hash = window.location.hash.substring(1);
      showTag(hash);
    } else {
      // Hide all sections when no hash
      tagSections.forEach(section => {
        section.classList.remove('active');
      });
      tagItems.forEach(item => {
        item.classList.remove('active');
      });
      postsContainer.classList.remove('show');
    }
  });
});
</script>