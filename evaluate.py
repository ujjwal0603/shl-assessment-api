import os
import re
import glob
from schemas import ChatRequest, Message
from agent import process_chat
import time

def parse_trace(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by Turn
    turns = re.split(r'### Turn \d+', content)[1:]
    
    conversation = []
    expected_urls_per_turn = []
    
    for turn in turns:
        # Extract user input
        user_match = re.search(r'> (.*?)\n', turn)
        if not user_match:
            continue
        user_text = user_match.group(1).strip()
        
        # Extract expected URLs from the agent's turn
        urls = re.findall(r'<(https://www\.shl\.com/products/product-catalog/view/.*?)>', turn)
        
        conversation.append(user_text)
        expected_urls_per_turn.append(urls)
        
    return conversation, expected_urls_per_turn

def evaluate_all():
    trace_files = glob.glob("GenAI_SampleConversations/*.md")
    
    total_expected = 0
    total_retrieved = 0
    total_correct = 0
    
    for trace_file in trace_files:
        print(f"\n--- Evaluating {os.path.basename(trace_file)} ---")
        user_inputs, expected_urls_per_turn = parse_trace(trace_file)
        
        messages = []
        for i, user_text in enumerate(user_inputs):
            messages.append(Message(role="user", content=user_text))
            
            try:
                # Add delay to avoid Groq rate limits
                time.sleep(2)
                response = process_chat(ChatRequest(messages=messages))
                
                # Append agent reply to history so context is maintained
                messages.append(Message(role="assistant", content=response.reply))
                
                # Compare recommendations
                expected_urls = expected_urls_per_turn[i]
                actual_urls = [r.url for r in response.recommendations]
                
                print(f"Turn {i+1}: User: '{user_text}'")
                if expected_urls:
                    print(f"  Expected {len(expected_urls)} URLs, got {len(actual_urls)}")
                    
                    total_expected += len(expected_urls)
                    total_retrieved += len(actual_urls)
                    
                    correct_in_turn = sum(1 for url in expected_urls if url in actual_urls)
                    total_correct += correct_in_turn
                    print(f"  Recall for turn: {correct_in_turn}/{len(expected_urls)}")
                else:
                    print(f"  Expected no URLs, got {len(actual_urls)}")
                    
            except Exception as e:
                print(f"  Error on turn {i+1}: {e}")

    print("\n=== FINAL EVALUATION ===")
    if total_expected > 0:
        recall = total_correct / total_expected
        print(f"Total Expected Recommendations: {total_expected}")
        print(f"Total Correct Recommendations: {total_correct}")
        print(f"Overall Recall: {recall:.2%}")
    else:
        print("No recommendations expected in any traces.")

if __name__ == "__main__":
    evaluate_all()
