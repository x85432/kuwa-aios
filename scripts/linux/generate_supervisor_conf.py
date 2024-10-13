import yaml
from jinja2 import Environment, Template

# Define the path to your YAML file
conf_data_file = "supervisor_conf.yaml"

# Define the template string
conf_template = """{% for item in program %}[program:ke-{{item['access_code']}}]
command={{cmd_prefix|safe}}{{item['cmd']|safe}} --access_code {{item['access_code']}} {{cmd_suffix|safe}}
directory={{item['working_dir']|default(working_dir)}}
environment={% if env is defined and env is not none %}{% for key, value in env.items() %}{{key}}={{value|safe}}{{ "," if not loop.last else "" }}{% endfor %}{% endif %}
numprocs={{item['num_procs']|default('1')}}
{% if user is defined %}user={{user}}{% endif %}
process_name=%(program_name)s_%(process_num)s
stopsignal=INT
redirect_stderr=true

{% endfor %}"""

if __name__ == '__main__':

    # Load the YAML data
    with open(conf_data_file, "r") as f:
        data = yaml.safe_load(f)

    # Create a Jinja2 environment
    env = Environment()

    # Create a template from the string
    template = Template(conf_template)

    # Render the template with the YAML data
    rendered_output = template.render(data)

    # Print the rendered output
    print(rendered_output)
