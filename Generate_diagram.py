import os
import subprocess

template_start = '@startuml\n!include /puml/Archimate.puml\n'
template_end = '\n@enduml'

content = 'Motivation_Stakeholder(StakeholderElement, "Stakeholder Description")'
file_content = template_start + content + template_end
file_name = 'diagram.puml'
java_cmd = ['java', '-jar', './puml/plantuml.jar', 'diagram.puml']

with open(file_name, 'w') as file:
    file.write(file_content)

if os.path.isfile(file_name):
    #os.system(java_cmd)
    subprocess.run(java_cmd, shell=True)
