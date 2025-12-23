# MyStocks项目归档文件记录

## 归档操作历史

### 2025-11-25 代码优化期间归档

#### 备份信息
- **备份日期**: 2025-11-25 14:43:19
- **备份位置**: /external-storage/mystocks-archive-20251125
- **备份内容**:
  - `.archive/` 目录（包含 old_code/, old_docs/, ARCHIVE_INDEX.md, sensitive-backups/）
  - `temp/` 目录（包含临时测试文件和freqtrade相关文件）
  - `tmp/` 目录（临时文件）
- **备份大小**: 估计约500MB+（主要来自temp目录）
- **备份原因**: 代码优化清理前的备份，用于版本管理和回滚

#### 可恢复方式

**恢复archive目录**:
```bash
# 如果需要恢复.archive目录
cp -r /external-storage/mystocks-archive-20251125/mystocks-archive-20251125/.archive /path/to/your/mystocks_spec/
```

**恢复temp目录（谨慎操作）**:
```bash
# 仅在需要调试时恢复，temp目录内容通常不需要
cp -r /external-storage/mystocks-archive-20251125/mystocks-archive-20251125/temp /path/to/your/mystocks_spec/
```

#### 清理前后对比

**清理前**:
- Python文件总数: 1862个
- temp目录项目数: 68,582个
- 备份文件数量: 27个
- 未跟踪文件: 76个

**预期清理后**:
- Python文件减少约20-30%
- 大文件数量显著减少
- 备份文件删除或移动到外部存储

#### 保留建议

1. **`.archive/old_code/`**: 保留，用于代码历史参考
2. **`.archive/old_docs/`**: 保留，用于文档历史参考
3. **`.archive/ARCHIVE_INDEX.md`**: 保留，用于索引查询
4. **`.archive/sensitive-backups/`**: 敏感信息备份，应安全存储
5. **`temp/`**: 可以完全清理，无业务影响
6. **`tmp/`**: 可以完全清理，无业务影响

#### 回滚方案

如果在代码优化过程中遇到问题，可以：

1. **分支回滚**:
   ```bash
   git checkout main
   git branch -D refactor/code-optimization-20251125
   ```

2. **从备份恢复**:
   ```bash
   # 恢复archive目录
   cp -r /external-storage/mystocks-archive-20251125/mystocks-archive-20251125/.archive /path/to/your/mystocks_spec/
   ```

3. **清理过程**:
   - 如需恢复临时文件，仅限调试目的
   - 原始Python文件已通过git管理，可以随时恢复

#### 安全注意事项

1. **敏感信息**: sensitive-backups目录包含敏感配置，请确保外部存储安全
2. **访问控制**: 限制外部存储路径的访问权限
3. **定期清理**: 建议每3个月清理一次过旧的备份

---

*此文件在代码优化过程中自动生成，记录备份和清理操作历史*
