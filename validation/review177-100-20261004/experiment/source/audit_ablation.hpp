#pragma once
#include <cstdlib>
#include <cstring>
namespace _home {
inline int AuditAblation() {
 static const int mode=[](){const char* s=std::getenv("RDFW_AUDIT_ABLATION");
  if(!s || !std::strcmp(s,"default"))return 0;
  if(!std::strcmp(s,"neutral"))return 1;
  if(!std::strcmp(s,"no_ask"))return 2;
  if(!std::strcmp(s,"legacy_visibility"))return 3;
  std::abort();}();return mode;
}
}
