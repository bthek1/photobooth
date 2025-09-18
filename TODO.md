# TODO

## ✅ Completed
- [x] Create REST API endpoints to replace Django forms
- [x] Add serializers for all models  
- [x] Create JavaScript API client
- [x] Update photobooth camera to use new API
- [x] Maintain backward compatibility

## 🔄 In Progress
- [ ] ~~remove the old html, js, css and forms~~ → Migrate all templates to use REST API
- [ ] ~~upgrade to react frontend~~ → Continue API-first approach for React readiness

## 📋 Next Steps
- [ ] save images to S3
- [ ] ability to download all images as zip
- [ ] ability to "delete" images (soft delete)
- [ ] second device like phone as controller
  - [ ] websocket connection to main device
- [ ] Complete form removal and template migration
- [ ] Add comprehensive API documentation (OpenAPI/Swagger)

## 🎯 Future Plans
```bash
# Frontend Migration Plan
- Upgrade to React frontend (API already ready)
- Use Material UI
- Use JWT for auth (already configured)
- Remove old HTML templates after React migration
```

## 📚 Documentation
- See `API_MIGRATION.md` for REST API usage
- See `.github/copilot-instructions.md` for development guidance