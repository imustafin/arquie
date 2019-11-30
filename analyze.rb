# Analyze Archimate model and save result as analysis.json

require 'nokogiri'
require 'json'

files = Dir.glob('./models/*.archimate')

puts "Analyzing #{files.length} models"

class Graph
  def initialize(doc)
    archimate = doc.xpath('//archimate:model').first
    @name = archimate[:name]

    nodes = archimate.xpath('//element[not(@source)]')
    
    @nodes = nodes.map do |x|
      {
        type: x[:'xsi:type'],
        id: x[:id],
        name: x[:name]
      }
    end

    relationships = archimate.xpath('//element[@source]')

    @relationships = relationships.map do |x|
      {
        type: x[:'xsi:type'],
        id: x[:id],
        source: x[:source],
        target: x[:target]
      }
    end
  end

  def empty_names
    @nodes.filter { |x| !x[:name] || x[:name].empty? }
  end

  def duplicate_names
    ans = []

    @nodes.each_with_index do |x, i|
      next if !x[:name] || x[:name].empty?

      @nodes.drop(i + 1).each do |y|
        ans << [x, y] if x[:name] == y[:name]
      end
    end

    ans
  end

  def isolated_nodes
    @nodes.filter do |x|
      @relationships.filter do |r|
        r[:source] == x[:id] || r[:target] == x[:id]
      end.empty?
    end
  end

  def node_types
    @nodes.map { |x| x[:type] }.uniq
  end

  def relationship_types
    @relationships.map { |x| x[:type] }.uniq
  end

  def node_by_id(id)
    @nodes.filter { |x| x[:id] == id }.first
  end

  def nodes_by_type(type)
    @nodes.filter { |x| x[:type] == type }
  end

  def find_relationship(source, type, target)
    @relationships.filter do |r|
      r[:source] == source && r[:type] == type && r[:target] == target
    end.first
  end

  def relationships_from_by_types(node_id, type, target_type)
    @relationships.filter do |r|
      r[:source] == node_id \
      && r[:type] == type \
      && node_by_id(r[:target])[:type] == target_type
    end
  end

  def missing_implied(a, ab, b, bc, c, ac_type)
    ans = []

    a_nodes = nodes_by_type(a)
    a_nodes.each do |a_node|
      ab_rels = relationships_from_by_types(a_node[:id], ab, b)

      b_nodes = ab_rels.map { |r| node_by_id(r[:target]) }
      b_nodes.each do |b_node|
        bc_rels = relationships_from_by_types(b_node[:id], bc, c)

        c_nodes = bc_rels.map { |r| node_by_id(r[:target]) }
        c_nodes.each do |c_node|
          ac_rel = find_relationship(a_node[:id], ac_type, c_node[:id])
          ans << {source: a_node, type: ac_type, target: c_node}
        end
      end
    end

    ans 
  end
end

APPLICATION_COMPONENT = 'archimate:ApplicationComponent'
APPLICATION_SERVICE = 'archimate:ApplicationService'
APPLICATION_INTERFACE = 'archimate:ApplicationInterface'
BUSINESS_PROCESS = 'archimate:BusinessProcess'
APPLICATION_FUNCTION = 'archimate:ApplicationFunction'

ASSIGNMENT_RELATIONSHIP = 'archimate:AssignmentRelationship'
SERVING_RELATIONSHIP = 'archimate:ServingRelationship'
COMPOSITION_RELATIONSHIP = 'archimate:CompositionRelationship'
REALIZATION_RELATIONSHIP = 'archimate:RealizationRelationship'

RULES = {
  app_service_serves_app: [
    APPLICATION_COMPONENT,
    ASSIGNMENT_RELATIONSHIP,
    APPLICATION_SERVICE,
    SERVING_RELATIONSHIP,
    APPLICATION_COMPONENT,
    SERVING_RELATIONSHIP
  ],

  app_service_serves_busproc: [
    APPLICATION_COMPONENT,
    ASSIGNMENT_RELATIONSHIP,
    APPLICATION_SERVICE,
    SERVING_RELATIONSHIP,
    BUSINESS_PROCESS,
    SERVING_RELATIONSHIP
  ],

  app_api_serves_app: [
    APPLICATION_COMPONENT,
    COMPOSITION_RELATIONSHIP,
    APPLICATION_INTERFACE,
    SERVING_RELATIONSHIP,
    APPLICATION_COMPONENT,
    SERVING_RELATIONSHIP
  ],

  app_func_realizes_service: [
    APPLICATION_COMPONENT,
    ASSIGNMENT_RELATIONSHIP,
    APPLICATION_FUNCTION,
    REALIZATION_RELATIONSHIP,
    APPLICATION_SERVICE,
    REALIZATION_RELATIONSHIP
  ],

  app_func_comp_func_assigned: [
    APPLICATION_COMPONENT,
    ASSIGNMENT_RELATIONSHIP,
    APPLICATION_FUNCTION,
    COMPOSITION_RELATIONSHIP,
    APPLICATION_FUNCTION,
    ASSIGNMENT_RELATIONSHIP
  ]
}

def analyze(f)
  doc = File.open(f) { |f| Nokogiri::XML(f) }
  g = Graph.new(doc)

  missing = []

  RULES.each do |k, v|
    miss = g.missing_implied(*v)
    miss.each do |m|
      missing << {type: k, relationship: m}
    end
  end

  violations = {
    empty_names: g.empty_names,
    duplicate_names: g.duplicate_names,
    isolated_nodes: g.isolated_nodes,
    missing_relationship: missing
  }

  violations 
end

# analyze('ArchiMetalSample.archimate')

analyzed = files.map { |f| analyze(f).merge(filename: f) }

File.open('analysis.json', 'w') do |f|
  f.write(JSON.pretty_generate(analyzed))
end
