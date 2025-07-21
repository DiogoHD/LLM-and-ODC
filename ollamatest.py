from ollama import chat
from ollama import ChatResponse

prompt = "What's the defect type of the orthogonal defect classification (ODC) in the following commit?"
commit = """diff --git a/fs/nfsd/nfs4acl.c b/fs/nfsd/nfs4acl.c
index b6ed38380ab805..54b8b4140c8f6e 100644
--- a/fs/nfsd/nfs4acl.c
+++ b/fs/nfsd/nfs4acl.c
@@ -443,7 +443,7 @@ init_state(struct posix_acl_state *state, int cnt)
 	 * enough space for either:
 	 */
 	alloc = sizeof(struct posix_ace_state_array)
-		+ cnt*sizeof(struct posix_ace_state);
+		+ cnt*sizeof(struct posix_user_ace_state);
 	state->users = kzalloc(alloc, GFP_KERNEL);
 	if (!state->users)
 		return -ENOMEM;"""

content = prompt + "\n" + commit

models = ["gemma3", "llama3.2", "mistral", "phi3"]
for model in models:
  response: ChatResponse = chat(model=model, messages=[
    {
      "role": "user",
      "content": content,
    },
  ])
  print("\n----------------------------------------------------")
  print(model)
  print("----------------------------------------------------")
  # print(response['message']['content'])
  # or access fields directly from the response object
  print(response.message.content)