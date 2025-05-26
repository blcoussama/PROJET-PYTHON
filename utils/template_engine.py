
import os
import re
from datetime import datetime

class TemplateEngine:
    def __init__(self, templates_dir="templates"):
        self.templates_dir = templates_dir

    def render(self, template_name, context=None):
        """Render a template with context"""
        if context is None:
            context = {}
        
        template_path = os.path.join(self.templates_dir, template_name)
        
        if not os.path.exists(template_path):
            return f"Template {template_name} not found"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Add helper functions to context
        context.update({
            'format_date': self.format_date,
            'truncate': self.truncate,
            'escape_html': self.escape_html
        })
        
        # Process template
        rendered = self.process_template(template_content, context)
        
        return rendered

    def process_template(self, template, context):
        """Process template with simple template syntax"""
        # Handle includes
        template = self.process_includes(template)
        
        # Handle conditionals
        template = self.process_conditionals(template, context)
        
        # Handle loops
        template = self.process_loops(template, context)
        
        # Handle variables
        template = self.process_variables(template, context)
        
        return template

    def process_includes(self, template):
        """Process {% include %} tags"""
        include_pattern = r'{%\s*include\s+["\']([^"\']+)["\']\s*%}'
        
        def replace_include(match):
            include_file = match.group(1)
            include_path = os.path.join(self.templates_dir, include_file)
            
            if os.path.exists(include_path):
                with open(include_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return f"<!-- Include {include_file} not found -->"
        
        return re.sub(include_pattern, replace_include, template)

    def process_conditionals(self, template, context):
        """Process {% if %} tags"""
        # Simple if/else/endif processing
        if_pattern = r'{%\s*if\s+([^%]+)\s*%}(.*?){%\s*endif\s*%}'
        
        def replace_if(match):
            condition = match.group(1).strip()
            content = match.group(2)
            
            # Split content on {% else %}
            parts = re.split(r'{%\s*else\s*%}', content)
            if_content = parts[0]
            else_content = parts[1] if len(parts) > 1 else ""
            
            # Evaluate condition
            if self.evaluate_condition(condition, context):
                return if_content
            else:
                return else_content
        
        return re.sub(if_pattern, replace_if, template, flags=re.DOTALL)

    def process_loops(self, template, context):
        """Process {% for %} tags"""
        for_pattern = r'{%\s*for\s+(\w+)\s+in\s+([^%]+)\s*%}(.*?){%\s*endfor\s*%}'
        
        def replace_for(match):
            var_name = match.group(1).strip()
            iterable_name = match.group(2).strip()
            loop_content = match.group(3)
            
            # Get iterable from context
            iterable = self.get_context_value(iterable_name, context)
            if not iterable:
                return ""
            
            result = []
            for i, item in enumerate(iterable):
                # Create loop context
                loop_context = context.copy()
                loop_context[var_name] = item
                loop_context['loop'] = {
                    'index': i,
                    'index0': i,
                    'first': i == 0,
                    'last': i == len(iterable) - 1
                }
                
                # Process loop content
                processed_content = self.process_template(loop_content, loop_context)
                result.append(processed_content)
            
            return ''.join(result)
        
        return re.sub(for_pattern, replace_for, template, flags=re.DOTALL)

    def process_variables(self, template, context):
        """Process {{ variable }} tags"""
        var_pattern = r'{{\s*([^}]+)\s*}}'
        
        def replace_var(match):
            var_name = match.group(1).strip()
            value = self.get_context_value(var_name, context)
            
            if value is None:
                return ""
            
            return str(value)
        
        return re.sub(var_pattern, replace_var, template)

    def evaluate_condition(self, condition, context):
        """Evaluate a simple condition"""
        # Remove 'not ' prefix
        negated = False
        if condition.startswith('not '):
            negated = True
            condition = condition[4:].strip()
        
        # Get value from context
        value = self.get_context_value(condition, context)
        
        # Evaluate truthiness
        result = bool(value)
        
        return not result if negated else result

    def get_context_value(self, path, context):
        """Get value from context using dot notation"""
        parts = path.split('.')
        value = context
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return None
            
            if value is None:
                break
        
        return value

    # Helper functions
    def format_date(self, date_str, format_str="%d/%m/%Y"):
        """Format date string"""
        try:
            if isinstance(date_str, str):
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                date_obj = date_str
            return date_obj.strftime(format_str)
        except:
            return date_str

    def truncate(self, text, length=100):
        """Truncate text to specified length"""
        if len(text) <= length:
            return text
        return text[:length] + "..."

    def escape_html(self, text):
        """Escape HTML characters"""
        if not isinstance(text, str):
            text = str(text)
        
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))