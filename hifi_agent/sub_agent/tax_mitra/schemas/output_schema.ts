/**
 * TypeScript types for Tax Mitra Agent output schema
 * Matches the Pydantic models in output_schema.py
 */

export type InputType =
	| "text"
	| "number"
	| "select"
	| "multiselect"
	| "date"
	| "email"
	| "tel"
	| "file";

export type Status = "success" | "error" | "pending" | "info";

export type Action = "input_required" | "processing" | "completed" | "error";

/**
 * Represents a single question with rich UI options
 */
export interface QuestionOption {
	/** The question text to display */
	title: string;

	/** Additional context or help text for the question */
	description?: string;

	/** The input type for the question */
	type: InputType;

	/** Available options for select/multiselect types */
	options?: string[];

	/** Whether this question must be answered */
	required: boolean;

	/** Default value for the field */
	default?: string;

	/** Placeholder text for the input */
	placeholder?: string;

	/** Pre-filled value if available */
	value?: string;

	/** Error message to display */
	error?: string;

	/** Minimum value for number inputs */
	min?: number;

	/** Maximum value for number inputs */
	max?: number;
}

/**
 * Progress information for multi-step processes
 */
export interface Progress {
	/** Current step number */
	current_step: number;

	/** Total number of steps */
	total_steps: number;

	/** Name/description of the current step */
	step_name: string;
}

/**
 * Main structured response format for Tax Mitra agent
 */
export interface TaxMitraResponse {
	/** The main response message to display to the user */
	message: string;

	/** Questions to ask the user - can be simple strings or rich question objects */
	questions?: string[] | QuestionOption[];

	/** Any additional data or results to display */
	data?: Record<string, any>;

	/** Status of the response */
	status?: Status;

	/** What action is expected next */
	action?: Action;

	/** Progress information for multi-step processes */
	progress?: Progress;
}

/**
 * Tax breakdown by income slabs
 */
export interface TaxBreakdown {
	up_to_250000?: number;
	"250001_to_500000"?: number;
	"500001_to_1000000"?: number;
	above_1000000?: number;
	[key: string]: number | undefined;
}

/**
 * Result of tax calculation
 */
export interface TaxCalculationResult {
	/** Total gross income */
	gross_income: number;

	/** Total taxable income after deductions and exemptions */
	taxable_income: number;

	/** Total tax liability */
	total_tax: number;

	/** Tax regime used (old or new) */
	tax_regime: string;

	/** Detailed breakdown of tax by slabs */
	breakdown: TaxBreakdown;

	/** Total deductions claimed */
	deductions?: number;

	/** Total exemptions claimed */
	exemptions?: number;
}

/**
 * Result of ITR form submission
 */
export interface ITRSubmissionResult {
	/** Acknowledgement number from tax department */
	acknowledgement_number: string;

	/** Date when ITR was submitted */
	submission_date: string;

	/** Type of ITR form used (ITR1, ITR2, etc.) */
	itr_form_type: string;

	/** Current status of the submission */
	status: string;

	/** Additional message or information */
	message: string;
}

/**
 * Result of refund tracking
 */
export interface RefundTrackingResult {
	/** Acknowledgement number of the filed ITR */
	acknowledgement_number: string;

	/** Refund amount if applicable */
	refund_amount?: number;

	/** Current status of the refund */
	refund_status: string;

	/** Expected date of refund credit */
	expected_date?: string;

	/** Any additional remarks */
	remarks?: string;
}

/**
 * Deduction details by sections
 */
export interface Deductions {
	"80C"?: number;
	"80D"?: number;
	"80E"?: number;
	"80G"?: number;
	"80EEA"?: number;
	"80CCD(1B)"?: number;
	standard_deduction?: number;
	hra_exemption?: number;
	[key: string]: number | undefined;
}

/**
 * Income source details
 */
export interface IncomeSource {
	/** Source of income (salary, business, etc.) */
	source: string;

	/** Amount from this source */
	amount: number;

	/** Additional details specific to the source */
	[key: string]: any;
}

/**
 * Complete tax data for ITR filing
 */
export interface TaxData {
	/** User's PAN number */
	pan: string;

	/** Assessment year */
	assessment_year: string;

	/** All income sources */
	income_sources: IncomeSource[];

	/** Total gross income */
	gross_income: number;

	/** Deductions claimed */
	deductions: Deductions;

	/** Taxable income */
	taxable_income: number;

	/** Tax regime chosen */
	tax_regime: "old" | "new";

	/** Total tax liability */
	total_tax: number;

	/** Tax already paid (TDS, advance tax, etc.) */
	tax_paid?: number;

	/** Any additional fields */
	[key: string]: any;
}

/**
 * Type guard to check if questions are QuestionOption objects
 */
export function isQuestionOptions(
	questions: string[] | QuestionOption[],
): questions is QuestionOption[] {
	return questions.length > 0 && typeof questions[0] === "object";
}

/**
 * Type guard to check if data contains tax calculation result
 */
export function isTaxCalculationResult(
	data: Record<string, any>,
): data is TaxCalculationResult {
	return (
		typeof data.gross_income === "number" &&
		typeof data.taxable_income === "number" &&
		typeof data.total_tax === "number" &&
		typeof data.tax_regime === "string"
	);
}

/**
 * Type guard to check if data contains ITR submission result
 */
export function isITRSubmissionResult(
	data: Record<string, any>,
): data is ITRSubmissionResult {
	return (
		typeof data.acknowledgement_number === "string" &&
		typeof data.submission_date === "string" &&
		typeof data.itr_form_type === "string"
	);
}

/**
 * Type guard to check if data contains refund tracking result
 */
export function isRefundTrackingResult(
	data: Record<string, any>,
): data is RefundTrackingResult {
	return (
		typeof data.acknowledgement_number === "string" &&
		typeof data.refund_status === "string"
	);
}
