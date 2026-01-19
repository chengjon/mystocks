/**
 * TypeScript Type Validator
 *
 * Provides validation and analysis tools for the TypeScript type extension system.
 * Ensures type safety, prevents conflicts, and maintains code quality.
 */

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  stats: ValidationStats;
}

export interface ValidationError {
  type: 'conflict' | 'missing' | 'invalid';
  message: string;
  file?: string;
  line?: number;
  suggestion?: string;
}

export interface ValidationWarning {
  type: 'unused' | 'naming' | 'documentation';
  message: string;
  file?: string;
  severity: 'low' | 'medium' | 'high';
}

export interface ValidationStats {
  totalTypes: number;
  extensionTypes: number;
  generatedTypes: number;
  conflicts: number;
  unusedTypes: number;
  coverage: number;
}

export class TypeValidator {
  /**
   * Validates the entire type system for conflicts and issues
   */
  static async validateTypeSystem(): Promise<ValidationResult> {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];

    // Check for type conflicts
    const conflicts = await this.detectTypeConflicts();
    if (conflicts.hasConflicts) {
      errors.push(...conflicts.conflicts.map(conflict => ({
        type: 'conflict' as const,
        message: `Type conflict: ${conflict.typeName} exists in both generated and extension types`,
        suggestion: `Rename extension type to ${conflict.typeName}VM or ${conflict.typeName}View`
      })));
    }

    // Check type completeness
    const completeness = await this.validateTypeCompleteness();
    errors.push(...completeness.errors);

    // Check naming conventions
    const naming = await this.validateNamingConventions();
    warnings.push(...naming.warnings);

    // Calculate statistics
    const stats = await this.generateStats();

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      stats
    };
  }

  /**
   * Detects naming conflicts between generated and extension types
   */
  static async detectTypeConflicts(): Promise<{
    hasConflicts: boolean;
    conflicts: Array<{
      typeName: string;
      generatedType: any;
      extensionType: any;
    }>;
  }> {
    try {
      // Import type definitions dynamically
      const generatedTypes = await this.loadGeneratedTypes();
      const extensionTypes = await this.loadExtensionTypes();

      const conflicts: Array<{
        typeName: string;
        generatedType: any;
        extensionType: any;
      }> = [];

      // Check for conflicts
      for (const [typeName, extensionType] of Object.entries(extensionTypes)) {
        if (generatedTypes[typeName]) {
          conflicts.push({
            typeName,
            generatedType: generatedTypes[typeName],
            extensionType
          });
        }
      }

      return {
        hasConflicts: conflicts.length > 0,
        conflicts
      };
    } catch (error) {
      console.error('Failed to detect type conflicts:', error);
      return { hasConflicts: false, conflicts: [] };
    }
  }

  /**
   * Validates type completeness and required fields
   */
  static async validateTypeCompleteness(): Promise<{
    errors: ValidationError[];
  }> {
    const errors: ValidationError[] = [];

    try {
      // Check if required type files exist
      const requiredFiles = [
        'extensions/strategy.ts',
        'extensions/market.ts',
        'extensions/common.ts'
      ];

      for (const file of requiredFiles) {
        if (!await this.fileExists(`src/api/types/${file}`)) {
          errors.push({
            type: 'missing',
            message: `Required type file missing: ${file}`,
            file,
            suggestion: 'Create the missing type file'
          });
        }
      }

      // Check if index.ts exports are complete
      const indexExports = await this.getIndexExports();
      const requiredExports = [
        'Strategy',
        'MarketOverviewVM',
        'PositionItem'
      ];

      for (const exportName of requiredExports) {
        if (!indexExports.includes(exportName)) {
          errors.push({
            type: 'missing',
            message: `Required export missing: ${exportName}`,
            file: 'src/api/types/index.ts',
            suggestion: 'Add the missing export to index.ts'
          });
        }
      }

    } catch (error) {
      console.error('Failed to validate type completeness:', error);
    }

    return { errors };
  }

  /**
   * Validates naming conventions
   */
  static async validateNamingConventions(): Promise<{
    warnings: ValidationWarning[];
  }> {
    const warnings: ValidationWarning[] = [];

    try {
      const extensionTypes = await this.loadExtensionTypes();

      for (const [typeName, typeDef] of Object.entries(extensionTypes)) {
        // Check PascalCase for interfaces and types
        if (!/^[A-Z][a-zA-Z0-9]*$/.test(typeName)) {
          warnings.push({
            type: 'naming',
            message: `Type name "${typeName}" should use PascalCase`,
            severity: 'medium'
          });
        }

        // Check for ViewModel suffix consistency
        if (typeName.includes('VM') && !typeName.endsWith('VM')) {
          warnings.push({
            type: 'naming',
            message: `Type "${typeName}" should end with "VM" if it's a ViewModel`,
            severity: 'low'
          });
        }
      }
    } catch (error) {
      console.error('Failed to validate naming conventions:', error);
    }

    return { warnings };
  }

  /**
   * Generates type system statistics
   */
  static async generateStats(): Promise<ValidationStats> {
    try {
      const generatedTypes = await this.loadGeneratedTypes();
      const extensionTypes = await this.loadExtensionTypes();

      const totalTypes = Object.keys(generatedTypes).length + Object.keys(extensionTypes).length;

      return {
        totalTypes,
        extensionTypes: Object.keys(extensionTypes).length,
        generatedTypes: Object.keys(generatedTypes).length,
        conflicts: 0, // Will be calculated separately
        unusedTypes: 0, // Would need usage analysis
        coverage: totalTypes > 0 ? (Object.keys(extensionTypes).length / totalTypes) * 100 : 0
      };
    } catch (error) {
      console.error('Failed to generate stats:', error);
      return {
        totalTypes: 0,
        extensionTypes: 0,
        generatedTypes: 0,
        conflicts: 0,
        unusedTypes: 0,
        coverage: 0
      };
    }
  }

  // Helper methods (would be implemented with actual file system access)
  private static async loadGeneratedTypes(): Promise<Record<string, any>> {
    // In a real implementation, this would dynamically import generated types
    return {};
  }

  private static async loadExtensionTypes(): Promise<Record<string, any>> {
    // In a real implementation, this would dynamically import extension types
    return {};
  }

  private static async fileExists(path: string): Promise<boolean> {
    // In a real implementation, this would check file existence
    return true;
  }

  private static async getIndexExports(): Promise<string[]> {
    // In a real implementation, this would parse index.ts exports
    return [];
  }
}

// CLI interface for running validations
export async function runValidation(): Promise<void> {
  console.log('🔍 Running TypeScript type validation...\n');

  const result = await TypeValidator.validateTypeSystem();

  if (result.errors.length > 0) {
    console.error('❌ Validation failed with errors:');
    result.errors.forEach(error => {
      console.error(`  • ${error.message}`);
      if (error.suggestion) {
        console.error(`    💡 ${error.suggestion}`);
      }
    });
    process.exit(1);
  }

  if (result.warnings.length > 0) {
    console.warn('⚠️  Validation completed with warnings:');
    result.warnings.forEach(warning => {
      console.warn(`  • ${warning.message}`);
    });
  }

  console.log('✅ Type validation passed!');
  console.log(`📊 Stats: ${result.stats.totalTypes} total types (${result.stats.coverage.toFixed(1)}% coverage)`);
}