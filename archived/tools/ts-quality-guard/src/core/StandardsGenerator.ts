/**
 * Standards Generator
 * Generates coding standards and best practices for different project types
 */

import { ProjectConfig } from '../types'

export class StandardsGenerator {
  /**
   * Generate coding standards for a project
   */
  static generateStandards(project: ProjectConfig): string {
    const standards = this.getBaseStandards()
    const projectSpecific = this.getProjectSpecificStandards(project)

    return this.formatStandards({ ...standards, ...projectSpecific })
  }

  /**
   * Generate AI coding prompt with standards
   */
  static generateAIPrompt(project: ProjectConfig, componentType?: string): string {
    const standards = this.generateStandards(project)
    const componentGuidance = componentType ? this.getComponentGuidance(componentType) : ''

    return `# TypeScript Coding Standards & Guidelines

## Project Context
- **Framework**: ${project.framework}
- **Type**: ${project.type}
- **TypeScript**: ${project.typescript}
- **Styling**: ${project.styling || 'N/A'}
- **State Management**: ${project.state || 'N/A'}
- **API Client**: ${project.api || 'N/A'}

## Coding Standards

${standards}

## Component-Specific Guidance

${componentGuidance}

## Critical Requirements
1. **Type Safety First**: Never use \`any\` unless absolutely necessary
2. **Interface Definitions**: Define proper interfaces for all data structures
3. **Error Handling**: Implement proper error boundaries and fallbacks
4. **Performance**: Consider performance implications of all decisions

## Code Quality Checklist
- [ ] TypeScript compilation passes without errors
- [ ] ESLint checks pass
- [ ] All interfaces are properly typed
- [ ] Error cases are handled appropriately
- [ ] Performance considerations addressed
- [ ] Code follows project conventions

Remember: Code quality is not optional - it's a fundamental requirement for maintainable software.`
  }

  /**
   * Get base coding standards applicable to all projects
   */
  private static getBaseStandards(): Record<string, any> {
    return {
      typescript: {
        strict: true,
        noImplicitAny: true,
        exactOptionalPropertyTypes: true,
        noUnusedLocals: false,
        noUnusedParameters: false
      },
      naming: {
        variables: 'camelCase',
        functions: 'camelCase',
        classes: 'PascalCase',
        interfaces: 'PascalCase',
        types: 'PascalCase',
        constants: 'UPPER_SNAKE_CASE'
      },
      structure: {
        maxFileLines: 300,
        maxFunctionLines: 50,
        maxClassLines: 200,
        importsOrder: ['external', 'internal', 'relative']
      },
      quality: {
        requiredJSDoc: true,
        preferInterfaces: true,
        avoidAny: true,
        explicitReturns: true
      }
    }
  }

  /**
   * Get project-specific standards
   */
  private static getProjectSpecificStandards(project: ProjectConfig): Record<string, any> {
    const standards: Record<string, any> = {}

    // Framework-specific standards
    switch (project.framework) {
      case 'vue3':
        standards.vue = {
          compositionApi: true,
          scriptSetup: true,
          componentNaming: 'PascalCase',
          propValidation: true,
          artDecoComponents: project.type === 'vue-frontend'
        }
        break

      case 'react':
        standards.react = {
          hooks: true,
          functionalComponents: true,
          componentNaming: 'PascalCase',
          propTypes: false, // Use TypeScript instead
          customHooks: true
        }
        break

      case 'angular':
        standards.angular = {
          modules: true,
          services: true,
          componentNaming: 'PascalCase',
          dependencyInjection: true
        }
        break
    }

    // API-specific standards
    if (project.api) {
      standards.api = {
        typedResponses: true,
        errorHandling: true,
        loadingStates: true,
        caching: project.api === 'react-query'
      }
    }

    // State management standards
    if (project.state) {
      standards.state = {
        typedStores: true,
        immutable: project.state === 'zustand',
        devtools: true,
        persistence: project.state === 'redux'
      }
    }

    return standards
  }

  /**
   * Get component-specific guidance
   */
  private static getComponentGuidance(componentType: string): string {
    const guidance: Record<string, string> = {
      'stat-card': `
### ArtDecoStatCard Component Guidelines

**Required Props:**
- \`label: string\` - Display label (required)
- \`value: string | number\` - Display value
- \`change?: number\` - Change percentage
- \`unit?: string\` - Value unit
- \`variant?: 'default' | 'rise' | 'fall' | 'gold'\` - Visual style

**Example:**
\`\`\`vue
<ArtDecoStatCard
  label="总收益"
  :value="totalProfit"
  :change="profitChange"
  unit="CNY"
  variant="rise"
/>
\`\`\`

**Best Practices:**
1. Always provide meaningful label
2. Use appropriate variant for data type
3. Handle loading states properly
4. Format large numbers appropriately`,

      'form': `
### Form Component Guidelines

**Validation:**
- Use reactive form validation
- Provide clear error messages
- Handle async validation properly

**Accessibility:**
- Proper labels for all inputs
- Keyboard navigation support
- Screen reader compatibility`,

      'table': `
### Data Table Guidelines

**Performance:**
- Implement virtual scrolling for large datasets
- Use pagination for server-side data
- Optimize re-renders with proper keys

**UX:**
- Sortable columns with visual indicators
- Filter functionality
- Export capabilities`
    }

    return guidance[componentType] || `
### General Component Guidelines

**Type Safety:**
- Define proper prop interfaces
- Use generic types where appropriate
- Handle optional props correctly

**Performance:**
- Use computed properties for derived data
- Implement proper lifecycle management
- Avoid unnecessary re-renders

**Maintainability:**
- Single responsibility principle
- Clear component naming
- Comprehensive documentation`
  }

  /**
   * Format standards as readable markdown
   */
  private static formatStandards(standards: Record<string, any>): string {
    let output = ''

    for (const [category, rules] of Object.entries(standards)) {
      output += `### ${category.charAt(0).toUpperCase() + category.slice(1)}\n\n`

      if (typeof rules === 'object') {
        for (const [rule, value] of Object.entries(rules)) {
          const checkmark = value ? '✅' : '❌'
          output += `- ${checkmark} **${rule}**: ${value}\n`
        }
      } else {
        output += `- ${rules}\n`
      }

      output += '\n'
    }

    return output.trim()
  }
}
