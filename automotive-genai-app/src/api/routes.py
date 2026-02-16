from flask import Blueprint, request, jsonify
from src.modules.orchestrator import VisualizationOrchestrator
import traceback

# Create blueprint for visualization routes
visualization_bp = Blueprint('visualization', __name__, url_prefix='/api')

# Initialize orchestrator
orchestrator = VisualizationOrchestrator(image_provider="dalle")


@visualization_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    validation = orchestrator.validate_configuration()
    return jsonify({
        "status": "healthy" if validation["all_configured"] else "degraded",
        "configuration": validation
    }), 200 if validation["all_configured"] else 206


@visualization_bp.route('/generate', methods=['POST'])
def generate_visualization():
    """
    Generate automotive visualization.
    
    Request body:
    {
        "design_prompt": "A sleek electric sports car...",
        "context": "Optional additional context",
        "enhance_image": false
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'design_prompt' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: 'design_prompt'"
            }), 400
        
        design_prompt = data.get('design_prompt')
        context = data.get('context')
        enhance_image = data.get('enhance_image', False)
        
        # Validate input
        if not design_prompt.strip():
            return jsonify({
                "success": False,
                "error": "Design prompt cannot be empty"
            }), 400
        
        # Generate visualization
        result = orchestrator.create_automotive_visualization(
            design_prompt=design_prompt,
            context=context,
            enhance_image=enhance_image
        )
        
        if not result.get('success'):
            return jsonify(result), 500
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500


@visualization_bp.route('/batch', methods=['POST'])
def batch_generate():
    """
    Generate multiple visualizations in batch.
    
    Request body:
    {
        "prompts": ["Prompt 1", "Prompt 2", ...],
        "context": "Optional shared context"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'prompts' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: 'prompts'"
            }), 400
        
        prompts = data.get('prompts')
        context = data.get('context')
        
        # Validate prompts
        if not isinstance(prompts, list) or len(prompts) == 0:
            return jsonify({
                "success": False,
                "error": "Prompts must be a non-empty list"
            }), 400
        
        # Generate visualizations
        results = orchestrator.batch_create_visualizations(
            prompts=prompts,
            context=context
        )
        
        return jsonify({
            "success": True,
            "count": len(results),
            "results": results
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


@visualization_bp.route('/image-prompt', methods=['POST'])
def generate_image_prompt():
    """
    Generate optimized image prompt from narrative.
    
    Request body:
    {
        "narrative": "Detailed design description..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'narrative' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: 'narrative'"
            }), 400
        
        narrative = data.get('narrative')
        
        result = orchestrator.llm_handler.generate_image_prompt(narrative)
        
        if not result.get('success'):
            return jsonify(result), 500
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


@visualization_bp.route('/narrative', methods=['POST'])
def generate_narrative():
    """
    Generate design narrative from prompt.
    
    Request body:
    {
        "prompt": "Design concept description...",
        "context": "Optional context"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: 'prompt'"
            }), 400
        
        prompt = data.get('prompt')
        context = data.get('context')
        
        result = orchestrator.llm_handler.generate_narrative(prompt, context)
        
        if not result.get('success'):
            return jsonify(result), 500
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


@visualization_bp.route('/config', methods=['GET'])
def get_config():
    """Get current configuration (sanitized)"""
    validation = orchestrator.validate_configuration()
    return jsonify({
        "image_provider": orchestrator.image_generator.provider,
        "image_model": orchestrator.image_generator.model,
        "llm_model": orchestrator.llm_handler.model,
        "validation": validation
    }), 200
