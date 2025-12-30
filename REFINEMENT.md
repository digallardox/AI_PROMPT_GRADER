# Message Refinement Feature

## Overview

All chat messages are now automatically refined for quality before being sent to users. This uses a constitutional AI approach to ensure responses are:

- **Empathetic** - Validates emotions and shows understanding
- **Actionable** - Provides helpful insights and next steps
- **Safe** - No harmful suggestions or dismissive language
- **Concise** - Under 500 characters, not overwhelming
- **Personality-consistent** - Matches companion traits

## How It Works

```
User message → /chat endpoint
                ↓
         Call Claude Sonnet (initial response)
                ↓
         [REFINEMENT STEP - AUTOMATIC]
                ↓
    Haiku evaluates on 5 criteria:
    1. Empathy (1-5 score)
    2. Actionability (1-5 score)
    3. Safety (pass/fail)
    4. Length (pass/fail)
    5. Personality match (pass/fail)
                ↓
    If score < 4 or any fail → Refine
    If already excellent → Return as-is
                ↓
         Return to user
```

## Configuration

### Current Settings (in .env)

```bash
ENABLE_REFINEMENT=true           # Feature flag (true/false)
```

### Advanced Settings (in app/config.py)

```python
refinement_model = "claude-3-5-haiku-20241022"  # Haiku for cost efficiency
refinement_max_tokens = 800                      # Max refined response length
refinement_temperature = 0.2                     # Lower = more consistent
refinement_timeout = 3.0                         # Circuit breaker (seconds)
```

## Running the Server

### With Refinement (Default)

```bash
make run
```

Output:
```
Starting server with message refinement enabled...
  ✓ ENABLE_REFINEMENT=true (configured in .env)
  ✓ Model: claude-3-5-haiku-20241022
  ✓ Timeout: 3.0s circuit breaker
```

### Without Refinement (For Testing)

```bash
make run-no-refine
```

Output:
```
Starting server WITHOUT message refinement...
  ✗ ENABLE_REFINEMENT=false (temporary override)
```

## Testing Refinement

### Test the Standalone Endpoint

```bash
curl -X POST http://localhost:8765/refine \
  -H "Content-Type: application/json" \
  -d '{
    "original_prompt": "You are Yuzu, a friendly AI companion.",
    "original_response": "That sounds hard. Try to be positive.",
    "criteria": {
      "max_length": 500,
      "tone": "warm",
      "personality_traits": ["Friendly", "Thoughtful", "Supportive"]
    }
  }'
```

Expected response:
```json
{
  "refined_response": "It sounds like you're going through something really difficult right now. When things feel tough, sometimes focusing on one small step can help. What's one tiny thing that might bring you a bit of relief?",
  "was_improved": true,
  "changes": ["Shortened by 15 characters", "Improved clarity and empathy"]
}
```

### Test the Integrated Chat Endpoint

```bash
curl -X POST http://localhost:8765/chat \
  -H "Content-Type: application/json" \
  -d '{
    "entryContent": "I had a frustrating day at work...",
    "message": "Why does this always happen to me?",
    "history": [],
    "companion": {
      "name": "Yuzu",
      "avatar": "🐨",
      "traits": ["Friendly", "Thoughtful", "Supportive"]
    }
  }'
```

The response will be automatically refined!

## Monitoring

### Check Server Logs

Look for these log messages:

**Refinement Enabled:**
```
INFO: Attempting to refine response
INFO: Response refined successfully (original: 450 chars, refined: 380 chars)
```

**Response Already Excellent:**
```
INFO: Response already excellent, no refinement needed
```

**Refinement Timeout (Fallback):**
```
WARNING: Refinement timeout after 3.0s, using original response
```

**Refinement Disabled:**
```
DEBUG: Refinement disabled, using original response
```

## Cost & Performance

### Cost Impact

- **Without refinement**: 1 Sonnet call per message
- **With refinement**: 1 Sonnet + 1 Haiku call
- **Total cost increase**: ~10-15% (Haiku is 20x cheaper than Sonnet)

### Performance Impact

- **Refinement latency**: 0.5-1 second (Haiku is fast)
- **Circuit breaker**: Caps max delay at 3 seconds
- **Fallback**: Original response if refinement times out
- **Net UX impact**: Minimal (users get better responses, slightly slower)

## Architecture Details

### Circuit Breaker Pattern

Refinement uses `asyncio.wait_for()` with a 3-second timeout:

```python
try:
    refinement_result = await asyncio.wait_for(
        refiner.refine(...),
        timeout=settings.refinement_timeout
    )
    # Use refined response
except asyncio.TimeoutError:
    # Use original response (graceful fallback)
```

### Evaluation Criteria

**Empathy (1-5)**:
- 5: Deeply empathetic with specific emotional reflection
- 3: Shows some understanding but generic
- 1: Dismissive or lacking empathy

**Actionability (1-5)**:
- 5: Specific, actionable guidance with clear next steps
- 3: Some suggestions but vague
- 1: No actionable insights, only platitudes

**Safety (Pass/Fail)**:
- FAIL: Dismisses feelings, suggests harm, gives medical advice
- PASS: Supportive, validating, focuses on emotional processing

**Length (Pass/Fail)**:
- FAIL: > 500 chars (overwhelming) or < 100 chars (dismissive)
- PASS: Concise but thorough

**Personality (Pass/Fail)**:
- FAIL: Generic ChatGPT voice without personality
- PASS: Maintains companion traits and distinctive voice

## Toggling Refinement

### Permanent Enable/Disable

Edit `.env` file:
```bash
# Enable
ENABLE_REFINEMENT=true

# Disable
ENABLE_REFINEMENT=false
```

Then restart server: `make run`

### Temporary Override (For Testing)

```bash
# Run without refinement (one-time)
make run-no-refine

# Or manually override
ENABLE_REFINEMENT=false make run
```

### Per-Request Override (Future Enhancement)

You could add a `skipRefinement` flag to the ChatRequest model:

```json
{
  "message": "Hello",
  "skipRefinement": true,  // Skip refinement for this message
  "companion": {...}
}
```

## API Documentation

### Endpoints

**POST /refine** - Standalone refinement endpoint
- Request: Original prompt + response + criteria
- Response: Refined response + metadata

**POST /chat** - Chat with automatic refinement
- Request: Message + history + companion settings
- Response: AI response (automatically refined if enabled)

### OpenAPI Docs

View full API documentation:
- **Swagger UI**: http://localhost:8765/docs
- **ReDoc**: http://localhost:8765/redoc

## Troubleshooting

### Refinement Not Working

1. Check `.env` file: `ENABLE_REFINEMENT=true`
2. Check server logs: Look for "Attempting to refine response"
3. Verify API key is set: `ANTHROPIC_API_KEY=sk-ant-...`

### Refinement Too Slow

1. Check timeout setting: `refinement_timeout` in `app/config.py`
2. Increase timeout: `REFINEMENT_TIMEOUT=5.0` in `.env`
3. Or disable for faster responses: `ENABLE_REFINEMENT=false`

### Refinement Not Improving Quality

1. Check logs: Is refinement being applied? ("was_improved: true")
2. Test standalone endpoint to see refinement prompt
3. Tune evaluation criteria in `refine_prompt_builder.py`
4. Add more examples to the refinement prompt

## Files Modified/Created

**New Files**:
- `app/models/refinement.py` - Data models
- `app/services/refiner_service.py` - Refinement service
- `app/services/prompts/refine_prompt_builder.py` - Prompts
- `app/routes/refine.py` - Refinement endpoint
- `REFINEMENT.md` - This documentation

**Modified Files**:
- `app/config.py` - Added refinement config
- `app/routes/chat.py` - Integrated refinement
- `app/main.py` - Registered refine router
- `.env` - Added ENABLE_REFINEMENT flag
- `Makefile` - Added refinement status messages

## Next Steps

1. **A/B Testing**: Enable for 50% of users, measure satisfaction
2. **Monitoring**: Track refinement rate, latency, quality scores
3. **Tuning**: Adjust evaluation criteria based on real data
4. **Caching**: Cache refined responses for similar messages
5. **Metadata**: Add refinement metadata to response (debug mode)

---

**Questions?** Check logs, test endpoints, or disable refinement temporarily for debugging.
